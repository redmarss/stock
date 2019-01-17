#!/bin/usr/env python
# -*- coding:utf-8 -*-

# AnalyzeBroker(tablename,startdate,enddate)
#
# (simulate_buy)(已在Broker类中实现)取得所有机构名称，模拟买入（第二天买，第三天卖），存入everydaysimulatebuy
#按照不同时间段（date）选出一定数量(top)的机构,存入数据库
#按照不同数据库中的机构进行模拟买入，并统计盈利


#NOET:1.删除best_broker，重新生成best_broker。2.跑数据，导出所有数据至U盘
#每月10日跑上一月数据
import myGlobal.myCls.mysqlCls as msql
import myGlobal.myCls.StockCls as mstock
import myGlobal.globalFunction as gf
import datetime
import Run.DailyRun as dr
import pandas as pd

class AnaylyzeBroker(object):
    #构造函数
    @gf.typeassert(startdate=str, enddate=str)
    def __init__(self, startdate, enddate):
        self._startdate = startdate
        self._enddate = enddate
        self._dbObject = msql.SingletonModel(host="localhost",port="3306",user="root",passwd="redmarss",db="tushare",charset="utf8")

    #通过平均值方式选取机构，count为时间段内交易次数，top为选前几名
    @gf.typeassert(count=int, top=int)
    def getTopBroker_avr(self,count=5, top=10):
        t = self._dbObject.fetchall(table="simulate_buy",
                          field="ts_date,broker_code,stock_code,buy_price,sell_price,amount,gainmoney,gainpercent",
                          where="ts_date between '%s' and '%s'"%(self._startdate,self._enddate))
        if len(t) == 0:
            print("没有模拟数据，找不到相关机构")
            return
        list_title = ['ts_date', 'broker_code', 'stock_code', 'buy_price', 'sell_price', 'amount', 'gainmoney',
                      'gainpercent']
        df = pd.DataFrame(list(t), columns=list_title)
        # 筛选出交易次数符合条件的机构
        s = df["broker_code"].value_counts() >= count
        s = s[s]  # 先把交易次数大于count的机构存入S
        dict_broker = s.to_dict()
        df = df[df["broker_code"].isin(list(dict_broker.keys()))]  # 再筛选出在机构列表中的数据
        # 能转换的都转换为数字
        df = df.apply(pd.to_numeric, errors='ignore')
        value = df.groupby(['broker_code'])['gainpercent'].mean()
        value = value.sort_values(ascending=False).head(top)
        li = list(value.to_dict().keys())
        return li




class BrokerSimulate(AnaylyzeBroker):
    #构造函数
    @gf.typeassert(reason=str)
    def __init__(self, startdate, enddate, date, reason):
        AnaylyzeBroker.__init__(self, startdate, enddate)             #也可写成super(Broker_Tosql,self).__init__()
        self._date = date
        self._reason = reason

    #将选出的机构存入best_broker表中，date为存入日期，reason为存入理由
    @gf.typeassert(li=list, date=str, reason=(str, type(None)))
    def list_toSql(self,li,date,reason=None):
        for broker_code in li:
            if gf.isBroker(broker_code):              #在broker_info中找到对应的机构代码
                broker_name = self._dbObject.fetchone(table="broker_info",field="broker_name",
                                                      where="broker_code='%s'"%broker_code)

                #去best_broker中去找是否已有重复数据
                result = self._dbObject.fetchall(table="best_broker",
                                                 where="broker_code='%s' and date='%s'"%(broker_code,date))
                if len(result)==0:
                    self._dbObject.insert(table="best_broker", broker_code=broker_code, broker_name=broker_name,
                                          date=date, reason=reason)
                else:
                    print("库中已有%s机构%s数据"%(broker_code,date))
        print("finished")

    def everyday_stock_record(self):
        start = datetime.datetime.strptime(self._startdate,"%Y-%m-%d").date()
        end = datetime.datetime.strptime(self._enddate,"%Y-%m-%d").date()
        tsdate = start
        while tsdate <= end:
            if gf.is_holiday(str(tsdate)) == False:
                #计算当天股票
                li_stock = dr.getStockEveryDay(str(tsdate))
                #存入数据库
                if len(li_stock) > 0:
                    for stock in li_stock:
                        self._everyday_stock_simulate_buy(tsdate,stock,1000)
            tsdate = tsdate + datetime.timedelta(days=1)

    @gf.typeassert(tsdate=str,stock=str,amount=(int,type(None)))
    def _everyday_stock_simulate_buy(self,tsdate,stock,reason,amount=None):
        money=float(10000)
        stock = gf._code_to_symbol(stock)
        if stock is None:
            return
        s = mstock.Stock(stock,tsdate)
        if s.open_price is not None:
            if amount is None:
                amount = (money//(s.open_price*100))*100
        gainmoeny = s.gainmoney(amount)
        if gainmoeny is None:               #第二天涨幅超过8%，无法买入
            return
        t = self._dbObject.fetchone(table="everyday_buy",where="ts_date='%s' and stock='%s'"%(tsdate,stock))
        if t is None:
            self._dbObject.insert(table="everyday_buy",ts_date=tsdate,stock=stock,amount=amount,gainmoney=gainmoeny,
                                  reason=reason)



def AnaylyzeHistory(start,end):
    date=datetime.datetime.strptime(start,"%Y-%m-%d").date()
    while date < datetime.datetime.strptime(end,"%Y-%m-%d").date():

        date = date+datetime.timedelta(days=1)


# def everyday_stock_record(startdate="2017-02-01",enddate="2018-12-20"):
#     if isinstance(startdate,str):
#         startdate = datetime.datetime.strptime(startdate,"%Y-%m-%d").date()
#     if isinstance(enddate,str):
#         enddate = datetime.datetime.strptime(enddate,"%Y-%m-%d").date()
#     date = startdate
#     while date<=enddate:
#         if gf.is_holiday(str(date)) == False:
#             #计算当天股票
#             li_stock = dr.getStockEveryDay(str(date))
#             #存入数据库
#             if len(li_stock) >0:
#                 for stock in li_stock:
#                     _everyday_stock_simulate_buy(date,stock,1000)
#         date = date + datetime.timedelta(days=1)

# def To_sql(li,reason=None):
#     dbObject = msql.SingletonModel(host="localhost", port="3306", user="root", passwd="redmarss", db="tushare",
#                                    charset="utf8")
#     li = map(lambda x: str(x), li)
#     for broker_code in li:
#         if gf.isBroker(broker_code):  # 在broker_info中找到对应的机构代码
#
#             broker_name = dbObject.fetchone(table="broker_info", field="broker_name",
#                                                   where="broker_code='%s'" % broker_code)[0]
#
#             # 去best_broker中去找是否已有重复数据
#             result = dbObject.fetchall(table="best_broker_list",
#                                              where="broker_code='%s'" % broker_code)
#             if len(result) == 0:
#                 dbObject.insert(table="best_broker_list", broker_code=broker_code, broker_name=broker_name,
#                                       reason=reason)
#             else:
#                 pass
#                 #print("库中已有%s机构%s数据" % (broker_code, date))
#     print("finished")

if __name__  == '__main__':
    everyday_stock_record(startdate="2018-01-01", enddate="2019-01-17")
    # li=getTopBroker_avr(3,20,"2019-01-01")
    # list_to_bestbrokerlist(li)
    # everyday_stock_record("2017-01-01","2019-01-31")


