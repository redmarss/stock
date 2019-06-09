#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.globalFunction as gf
from myGlobal.myCls.mylogger import mylogger
from myGlobal.myCls.Stock import Stock
import myGlobal.myTime as myTime
import datetime
from myGlobal.myCls.multiProcess import threads

#判断一个股票前一天涨停、后一天跌停的情况下，一个月后涨幅
def _OneMonth(stock_code):
    startdate="2017-01-01"
    enddate= "2019-05-06"
    date = myTime.strTodate(startdate)
    while date<=myTime.strTodate(enddate):
        print(str(date))
        ts_date = str(date)
        if gf.is_holiday(ts_date):
            date = date + datetime.timedelta(days=1)
            continue
        s = Stock(stock_code,ts_date)
        s_list = s.next_some_days(2)
        if s_list!=2:
            return
        if gf.isLimit(stock_code,s_list[0].open_price,s_list[0].close_price,flag=1) and gf.isLimit(stock_code,s_list[1].open_price,s_list[1].close_price,flag=-1):
            mylogger(filepath='\code.log').info("%s于%s触发成功"%(stock_code,ts_date))
        print("%s完成"%ts_date)
        date = date+datetime.timedelta(days=1)

#@threads(10)
def Run():
    #stock_list = gf.getAllStockFromTable()
    stock_list=['sh603383']
    [_OneMonth(code) for code in stock_list]

if __name__ == '__main__':
    Run()






