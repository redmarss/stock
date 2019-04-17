#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.globalFunction as gf
from myGlobal.myCls.msql import DBHelper
from myGlobal.myCls.SimulateCls import BrokerSimulate
import myGlobal.myTime as mTime
from myGlobal.myCls.StockCls import Stock
import datetime
import Run.DailyRun as DailyRun

class Broker(BrokerSimulate):

    #构造函数，参数为broker_code
    def __init__(self,broker_code,ts_date):
        self.broker_code = broker_code
        self.ts_date = ts_date
        self.stocklist = self._getBuyStock()
        self.stockpricelist = None







    #获取某个日期，broker_code购买的股票列表
    def _getBuyStock(self):
        li_buy_stock = []
        sql_brokerbuy = '''select a.stock_code from 
                        broker_buy_stock_info as a,broker_buy_summary as b
                        where a.broker_buy_summary_id=b.id and b.broker_code="%s" and b.ts_date="%s"'''%(self.broker_code,self.ts_date)

        t_broker_buy = DBHelper().fetchall(sql_brokerbuy)
        if len(t_broker_buy) > 0:
            for stock in t_broker_buy:
                stock = gf.code_to_symbol(str(stock[0]))
                if stock not in li_buy_stock:
                    li_buy_stock.append(stock)
        return li_buy_stock




    #模拟买入并写入数据库
    def simulate(self,tablename,ts_date,amount=1000,ftype=1):

        if len(self.stocklist) > 0:
            for stock_code in self.stocklist:
                #调用simulatebuy函数，如果没有，调用父函数（BrokerSimulate）的
                self.simulatebuy(tablename,stock_code,ts_date,amount,ftype)
        else:
            print("%s机构%s没有买入股票" % (self.broker_code,self.ts_date))

    #根据ts_date为机构打分，返回具体分值
    def score(self,start='2017-01-01'):
        #如果当天机构没有交易数据，记0分
        if len(self.stocklist) == 0:
            return 0
        #取出数据库中当前的score值
        sql = "select score from broker_info where broker_code='%s'" % self.broker_code
        score = DBHelper().execute(sql)[0]









