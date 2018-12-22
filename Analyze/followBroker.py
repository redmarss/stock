#!/bin/usr/env python
# -*- coding:utf-8 -*-

#每月10日跑上一月数据
import myGlobal.myCls.mysqlCls as msql
import myGlobal.myCls.StockCls as mstock
import myGlobal.globalFunction as gf
import myGlobal.myCls.BrokerCls as mbroker
import pandas as pd

def simulate_buy(startdate='2017-01-01',enddate='2018-12-31', amount=1000):
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare',
                                   charset='utf8')
    d = dbObject.fetchall(table="broker_buy_summary", field="broker_code,ts_date",
                          where="ts_date between '%s' and '%s' order by ts_date"%(startdate,enddate))
    for i in range(len(d)):
        broker_code = d[i][0]
        ts_date = str(d[i][1])
        b = mbroker.Broker(broker_code,ts_date)              #日期参数必须为str类型
        b.simulate_buy(amount)


def getTopBroker_avr():
    dbObject = msql.SingletonModel(host="localhost",port="3306",user="root",passwd="redmarss",db="tushare",charset="utf8")
    t = dbObject.fetchall(table="simulate_buy",
                          field="ts_date,broker_code,stock_code,buy_price,sell_price,amount,gainmoney,gainpercent")


if __name__ =='__main__':
    simulate_buy("2017-01-01","2018-11-30",1000)
    # dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare',
    #                                charset='utf8')
    # t = dbObject.fetchall(table="simulate_buy",
    #                       field="ts_date,broker_code,stock_code,buy_price,sell_price,amount,gainmoney,gainpercent")
    # list_title = ['ts_date','broker_code','stock_code','buy_price','sell_price','amount','gainmoney','gainpercent']
    # df = pd.DataFrame(list(t),columns=list_title)
    # df=df.sort_values(axis=0,by='broker_code',ascending='False')
    # df = df.apply(pd.to_numeric, errors='ignore')
    # value=df.groupby(['broker_code'])['gainpercent'].count()
    # value = value.sort_values(ascending=False)
    # print(value)


