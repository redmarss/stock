#!/usr/bin/env python
# -*-coding:utf8-*-
import myGlobal.myCls.AnalyzeBrokerCls as AnalyzeBroker
import myGlobal.globalFunction as gf
import myGlobal.myCls.StockCls as mstock
import datetime

class BrokerSimulate(AnalyzeBroker):
    #构造函数
    @gf.typeassert(reason=str)
    def __init__(self, startdate, enddate, date, reason):
        AnalyzeBroker.__init__(self, startdate, enddate)             #也可写成super(Broker_Tosql,self).__init__()
        self._date = date
        self._reason = reason


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
                    self._everyday_stock_simulate_buy(str(tsdate),stock,1000)
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
    gainmoeny = s.gainmoney(int(amount))
    if gainmoeny is None:               #第二天涨幅超过8%，无法买入
        return
    t = self._dbObject.fetchone(table="everyday_buy",where="ts_date='%s' and stock='%s'"%(tsdate,stock))
    if t is None:
        self._dbObject.insert(table="everyday_buy",ts_date=tsdate,stock=stock,amount=amount,gainmoney=gainmoeny,
                              reason=reason)
