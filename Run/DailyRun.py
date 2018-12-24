#!/bin/usr/env python
# -*-coding:utf-8 -*-
import datetime
import myGlobal.globalFunction as gf
import myGlobal.myCls.mysqlCls as msql
#每日8.50分运行
def getStockEveryDay():
    date = str(datetime.datetime.today().date())
    dbObject = msql.SingletonModel(host='localhost', port='3306',
                                         user='root', passwd='redmarss',
                                         charset='utf8', db='tushare')
    if gf.is_holiday(str(date)) == False:           #交易日
        tbroker = dbObject.fetchall(table="best_broker_list",field="broker_code")
        libroker = [i[0] for i in tbroker]
        for i in range(len(libroker)):
            dbObject.fetchall()

if __name__ == "__main__":
    getStockEveryDay()