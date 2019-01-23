#!/usr/bin/env python
# -*-coding:utf8-*-

import myGlobal.globalFunction as gf
import myGlobal.myCls.StockCls as mstock
import myGlobal.myCls.mysqlCls as msql
import myGlobal.myTime as mTime
import datetime
import Run.DailyRun as DailyRun

class Simulate(object):
    #构造函数
    @gf.typeassert(startdate=str, enddate=str)
    def __init__(self, startdate, enddate):
        if mTime.isDate(startdate) is True and mTime.isDate(enddate) is True:
            self.startdate = startdate
            self.enddate = enddate
        else:
            print("输入的日期参数不合法")
            return
        self.dbObject = msql.SingletonModel(host="localhost",port="3306",user="root",passwd="redmarss",db="tushare",charset="utf8")

    #根据输入的机构表，记录这些机构模拟买卖信息
    gf.typeassert(table=str,where=str,reason=str)
    def everyday_stock_record(self,table,where,reason):
        li_broker = []
        try:                #判断table是否合法
            t = self.dbObject.fetchall(field="broker_code", table=table, where=where)
            for i in range(len(t)):
                li_broker.append(str(t[i][0]))              #将选出的broker_code以str方式放入li_broker
        except:
            print("数据库参数有误，请重新输入")
            return
        start = datetime.datetime.strptime(self.startdate, "%Y-%m-%d").date()
        end = datetime.datetime.strptime(self.enddate, "%Y-%m-%d").date()
        tsdate = start
        while tsdate <= end:
            if gf.is_holiday(str(tsdate)) is False:
                li_stock = []
                #计算当天股票
                t1 = DailyRun.getStockEveryDay(str(tsdate))
                for i in range(len(t1)):
                    li_stock.append(str(t1[i][0]))
                #存入数据库
                if len(li_stock) > 0:
                    for stock in li_stock:
                        self._everyday_stock_simulate_buy(str(tsdate), stock, reason, 1000)
            tsdate = tsdate + datetime.timedelta(days=1)

    @gf.typeassert(tsdate=str,stock=str,amount=(int,type(None)), money=float)
    def _everyday_stock_simulate_buy(self, tsdate, stock, reason, amount=None, money=10000.0):     #若数量为空，则根据money除以股价计算amount
        stock = gf._code_to_symbol(stock)
        if stock is None:
            return
        st = mstock.Stock(stock, tsdate)
        if st.open_price is not None:
            if amount is None:
                amount = int((money//(st.open_price*100))*100)
        gainmoeny = st.gainmoney(amount)
        if gainmoeny is None:               #第二天涨幅超过8%，无法买入
            return
        t = self._dbObject.fetchone(table="everyday_buy",where="ts_date='%s' and stock='%s'"%(tsdate,stock))
        if t is None:
            self._dbObject.insert(table="everyday_buy",ts_date=tsdate,stock=stock,amount=amount,gainmoney=gainmoeny,
                                  reason=reason)


s = Simulate("2017-01-01","2017-12-31")
s.everyday_stock_record("best_broker_list","true")
