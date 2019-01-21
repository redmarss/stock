#!/bin/usr/env python
# -*-coding:utf-8 -*-
import myGlobal.myTime as mt
import datetime
import myGlobal.globalFunction as gf
import myGlobal.myCls.mysqlCls as msql
#每晚18点后手动运行或第二天8.50分自动运行
@gf.typeassert(date=(str,type(None)),count=int)
def getStockEveryDay(date=None, count=32):
    if date is None:        #如果不输入日期，则获取默认日期
        if mt.get_hour() > 18:          #每日18点后运行，则日期定义为“当天”，否则，取昨天
            date = str(datetime.datetime.today().date())
        else:
            date = str(datetime.datetime.today().date()-datetime.timedelta(days=1))
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root',
                                   passwd='redmarss', charset='utf8', db='tushare')
    listock=list()
    if gf.is_holiday(str(date)) is False:           #交易日
        sql= '''select a.stock_code,a.stock_name,b.broker_name,b.ts_date from broker_buy_stock_info as a,broker_buy_summary as b 
        where a.broker_buy_summary_id =b.id and ts_date="%s" and 
        b.broker_code in (select broker_code from best_broker_list)''' % date
        t = dbObject.execute(sql)
        print(len(t))
        return t
    else:
        print("所输入日期非交易日")
        return


if __name__ == "__main__":
    print(getStockEveryDay("2019-01-21"))