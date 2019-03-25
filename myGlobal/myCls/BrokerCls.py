#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.globalFunction as gf
from myGlobal.myCls.msql import DBHelper
import myGlobal.myTime as mTime
from myGlobal.myCls.StockCls import Stock
import datetime
import Run.DailyRun as DailyRun

class Broker(object):

    #构造函数，参数为broker_code
    def __init__(self,broker_code,ts_date):
        self.broker_code = broker_code
        self.ts_date = ts_date
        self.dbHelper = DBHelper()
        self.dbHelper.connectDatabase()


    #获取某个日期，broker_code购买的股票列表
    def getBuyStock(self):
        li_buy_stock = []
        sql_brokerbuy = '''select a.stock_code from 
                        broker_buy_stock_info as a,broker_buy_summary as b
                        where a.broker_buy_summary_id=b.id and b.broker_code="%s" and b.ts_date="%s"'''%(self.broker_code,self.ts_date)
        print(self.dbHelper)
        t_broker_buy = self.dbHelper.fetchall(sql_brokerbuy)
        if len(t_broker_buy) > 0:
            for stock in t_broker_buy:
                stock = gf.code_to_symbol(str(stock[0]))
                if stock not in li_buy_stock:
                    li_buy_stock.append(stock)
        return li_buy_stock







