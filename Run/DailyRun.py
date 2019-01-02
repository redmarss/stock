#!/bin/usr/env python
# -*-coding:utf-8 -*-
import datetime
import myGlobal.globalFunction as gf
import myGlobal.myCls.mysqlCls as msql
#每日8.50分运行
def getStockEveryDay(date=None):
    if date is None:
        date = str(datetime.datetime.today().date()+datetime.timedelta(days=-1))
    dbObject = msql.SingletonModel(host='localhost', port='3306',
                                         user='root', passwd='redmarss',
                                         charset='utf8', db='tushare')
    listock=list()
    if gf.is_holiday(str(date)) == False:           #交易日
        tbroker = dbObject.fetchall(table="best_broker_list",field="broker_code")
        libroker = [i[0] for i in tbroker]
        for i in range(len(libroker)):
            tstock = dbObject.fetchall(table="broker_buy_stock_info as a,broker_buy_summary as b",
                              field="stock_code",
                              where="b.id=a.broker_buy_summary_id and broker_code='%s' and ts_date='%s'"%(libroker[i],date))
            for j in range(len(tstock)):
                if tstock[j] not in listock:
                    listock.append(tstock[j][0])
    return listock

if __name__ == "__main__":
    print(getStockEveryDay("2018-12-28"))