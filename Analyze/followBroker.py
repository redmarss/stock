#!/bin/usr/env python
# -*- coding:utf-8 -*-

#每月10日跑上一月数据
import myGlobal.myCls.mysqlCls as msql
import myGlobal.myCls.StockCls as mstock
import myGlobal.globalFunction as gf

import pandas as pd




def getTopBroker_avr(count=5):
    dbObject = msql.SingletonModel(host="localhost",port="3306",user="root",passwd="redmarss",db="tushare",charset="utf8")
    t = dbObject.fetchall(table="simulate_buy",
                          field="ts_date,broker_code,stock_code,buy_price,sell_price,amount,gainmoney,gainpercent")
    list_title = ['ts_date', 'broker_code', 'stock_code', 'buy_price', 'sell_price', 'amount', 'gainmoney',
                  'gainpercent']
    df = pd.DataFrame(list(t), columns=list_title)
    # 筛选出交易次数符合条件的机构
    s = df["broker_code"].value_counts()>=count
    s = s[s]                                        #先把交易次数大于count的机构存入S
    dict_broker = s.to_dict()
    df = df[df["broker_code"].isin(list(dict_broker.keys()))]       #再筛选出在机构列表中的数据
    #能转换的都转换为数字
    df = df.apply(pd.to_numeric, errors='ignore')
    value = df.groupby(['broker_code'])['gainpercent'].mean()
    value = value.sort_values(ascending=False)
    print(value)

if __name__ =='__main__':
    getTopBroker_avr()
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


