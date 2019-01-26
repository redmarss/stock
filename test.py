#!/bin/usr/env python
# -*- coding:utf-8 -*-

import myGlobal.myCls.msql as msql
import datetime
import Analyze.AnaylyzeBroker as fb
import myGlobal.globalFunction as gf
import  Run.DailyRun as dr
import myGlobal.myCls.Stock as mstock

def _everyday_stock_simulate_buy(tsdate,stock,amount=None):
    money=float(10000)
    if not isinstance(tsdate,str):
        tsdate = str(tsdate)
    stock = gf.code_to_symbol(stock)
    if stock is None:
        return
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss',
                                   charset='utf8', db='tushare')
    s = mstock.Stock(str(stock),tsdate)
    if s.open_price is not None:
        if amount is None:
            amount = (money//(s.open_price*100))*100
    gainmoeny = s.gainmoney(amount)
    if gainmoeny is None:               #第二天涨幅超过8%，无法买入
        return
    t = dbObject.fetchone(table="test_simulate_buy",where="ts_date='%s' and stock='%s'"%(tsdate,stock))
    if t is  None or len(t)==0:
        dbObject.insert(table="test_simulate_buy",ts_date=tsdate,stock=stock,amount=amount,gainmoney=gainmoeny)


def getStockEveryDay(date=None,count=32):
    if date is None:
        date = str(datetime.datetime.today().date()+datetime.timedelta(days=-1))

    listock=list()
    if gf.is_holiday(str(date)) == False:           #交易日
        libroker = fb.getTopBroker_avr(1, 20, "2019-01-01")
        for i in range(len(libroker)):
            tstock = dbObject.fetchall(table="broker_buy_stock_info as a,broker_buy_summary as b",
                              field="stock_code",
                              where="b.id=a.broker_buy_summary_id and broker_code='%s' and ts_date='%s'"
                                    %(libroker[i],date))
            for j in range(len(tstock)):
                if tstock[j][0] not in listock:
                    listock.append(tstock[j][0])
    return listock



dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss',
                               charset='utf8', db='tushare')
startdate=datetime.datetime.strptime("2019-01-01","%Y-%m-%d").date()
enddate = datetime.datetime.today().date()
date = startdate
while date <= enddate:
    if gf.is_holiday(str(date)) == False:
        # 计算当天股票
        li_stock = getStockEveryDay(str(date))
        print(li_stock,str(date))

        # 存入数据库
        if len(li_stock) > 0:
            for stock in li_stock:
                _everyday_stock_simulate_buy(str(date), str(stock), 1000)
    date = date + datetime.timedelta(days=1)