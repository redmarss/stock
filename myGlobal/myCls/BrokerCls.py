#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.globalFunction as gf
from myGlobal.myCls.msql import DBHelper
from myGlobal.myCls.SimulateCls import BrokerSimulate
import myGlobal.myTime as mTime
from myGlobal.myCls.Stock import Stock
import datetime
import Run.DailyRun as DailyRun

class Broker(object):

    #构造函数，参数为broker_code
    def __init__(self,broker_code,ts_date):
        self._broker_code = broker_code
        self._ts_date = ts_date
        self._stocklist = []                #self._getBuyStock()

    #获取该日期broker_code购买的股票列表
    def _getBuyStock(self):
        #查询当天该机构购买的股票列表
        sql_brokerbuy = f'''SELECT * FROM 
                            broker_buy_stock_info info
                            INNER JOIN
                            broker_buy_summary summary 
                            ON info.broker_buy_summary_id = summary.id
                            WHERE
                            summary.broker_code = '{self._broker_code}'
                            AND summary.ts_date = '{self._ts_date}';'''
        t_broker_buy = DBHelper().fetchall(sql_brokerbuy)
        if len(t_broker_buy) > 0:
            for stock in t_broker_buy:
                stock = gf.code_to_symbol(str(stock[0]))
                if stock not in self._stocklist:
                    self._stocklist.append(stock)





    # #模拟买入并写入数据库
    # def simulate(self,tablename,ts_date,amount=1000,ftype=1):
    #
    #     if len(self.stocklist) > 0:
    #         for stock_code in self.stocklist:
    #             #调用simulatebuy函数，如果没有，调用子函数（BrokerSimulate）的
    #             self.simulatebuy(tablename,stock_code,ts_date,amount,ftype)
    #     else:
    #         print("%s机构%s没有买入股票" % (self.broker_code,self.ts_date))
    #
    # # 根据ts_date，计算日期前所有模拟交易的分值，并返回最终分数写入数据库
    # def score(self,ftype=1):
    #     #获取simulate表中，该日期前该机构的得分，存入一个List中
    #     sql = "select getscore from simulate where broker_code='%s' and ts_date<='%s'" %(self.broker_code,self.ts_date)
    #     score_list = []
    #     t = DBHelper().execute(sql)
    #     for i in range(len(t)):
    #         score_list.append(t[i][0])
    #     print(score_list)









