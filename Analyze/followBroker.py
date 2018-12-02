#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.mysqlCls as msql

#输入机构代码，日期，返回元组
#（broker_code,ts_date,[stock_list]）
def getStockCode(broker_code = None,ts_date = None):
    dbObject = msql.SingletonModel(host='localhost',port='3306',user='root',passwd='redmarss',db='tushare',charset='utf8')
    d = dbObject.fetchall(table='broker_buy_stock_info as a,broker_buy_summary as b',
                          field='a.stock_code',
                          where='a.broker_buy_summary_id=b.id and b.broker_code="%s" and b.ts_date="%s"' % (broker_code, ts_date))
    wantbuy_list = [item['stock_code'][:6] for item in d]
    return broker_code, ts_date, wantbuy_list


def buy_stock(t):
    #判断传入参数是否合规
    if not isinstance(t, tuple) or not isinstance(t[2], list):
        print("传入参数有误")
        return
