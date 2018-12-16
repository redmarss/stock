#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.mysqlCls as msql
import myGlobal.myCls.StockCls as mstock
import myGlobal.globalFunction as gf
import myGlobal.myCls.BrokerCls as mbroker

if __name__ =='__main__':
    dbObject = msql.SingletonModel(host='localhost',port='3306',user='root',passwd='redmarss',db='tushare',charset='utf8')
    d = dbObject.fetchall(table="broker_buy_summary", field="broker_code,ts_date", where="ts_date<='2017-01-31'")
    for i in range(len(d)):
        b=mbroker.Broker(d[i][0],str(d[i][1]))              #日期参数必须为str类型
        b.simulate_buy(1000)



