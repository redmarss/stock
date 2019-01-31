#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.globalFunction as gf
import myGlobal.myCls.msql as msql
import myGlobal.myTime as mTime
from myGlobal.myCls.Stock import Stock
import datetime
import Run.DailyRun as DailyRun

class Broker(object):

    #构造函数，参数为broker_code
    def __init__(self,broker_code):
        #判断机构代码是否在broker_info表中
        if gf.isBroker(broker_code) is True:
            self.broker_code = broker_code
            self.dbObject = msql.SingletonModel(host='localhost', port='3306',
                                       user='root', passwd='redmarss',
                                       charset='utf8',db='tushare')
        else:
            print("机构代码%s不在broker_info表中，请重试" % broker_code)
            self.broker_code = None
            return


    #获取某个日期，broker_code购买的股票列表
    def getBuyStock(self, ts_date):
        li_buy_stock = []
        if self.broker_code is not None:
            if gf.is_holiday(ts_date) is False:
                t_broker_buy = self.dbObject.fetchall(table='broker_buy_stock_info as a,broker_buy_summary as b',
                                                      field='a.stock_code',
                                                      where='a.broker_buy_summary_id=b.id and b.broker_code="%s" and b.ts_date="%s"'
                                                            % (self.broker_code, ts_date))
                if len(t_broker_buy) > 0:
                    for stock in t_broker_buy:
                        stock = gf.code_to_symbol(str(stock[0]))
                        if gf.isStockA(stock) and stock not in li_buy_stock:
                            li_buy_stock.append(stock)
            else:
                pass
        return li_buy_stock







