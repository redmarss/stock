#!/usr/bin/env python
# -*- coding:utf-8 -*-
import myGlobal.globalFunction as gf
import myGlobal.myCls.mysqlCls as msql
import pandas as pd

class AnalyzeBroker(object):
    #构造函数
    @gf.typeassert(startdate=str, enddate=str)
    def __init__(self, startdate, enddate):
        self._startdate = startdate
        self._enddate = enddate
        self._dbObject = msql.SingletonModel(host="localhost",port="3306",user="root",passwd="redmarss",db="tushare",charset="utf8")

    #通过平均值方式选取机构，count为时间段内交易次数，top为选前几名
    @gf.typeassert(count=int, top=int)
    def getTopBroker_avr(self,count=5, top=30):
        #从simulate_buy中取（第一天买第二天卖）
        t = self._dbObject.fetchall(table="simulate_buy",
                          field="ts_date,broker_code,stock_code,buy_price,sell_price,amount,gainmoney,gainpercent",
                          where="ts_date between '%s' and '%s'"%(self._startdate,self._enddate))
        if len(t) == 0:
            print("没有模拟数据，找不到相关机构")
            return
        list_title = ['ts_date', 'broker_code', 'stock_code', 'buy_price', 'sell_price', 'amount', 'gainmoney',
                      'gainpercent']
        df = pd.DataFrame(list(t), columns=list_title)
        # 筛选出交易次数符合条件的机构
        s = df["broker_code"].value_counts() >= count
        s = s[s]  # 先把交易次数大于count的机构存入S
        dict_broker = s.to_dict()
        df = df[df["broker_code"].isin(list(dict_broker.keys()))]  # 再筛选出在机构列表中的数据
        # 能转换的都转换为数字
        df = df.apply(pd.to_numeric, errors='ignore')
        value = df.groupby(['broker_code'])['gainpercent'].mean()
        value = value.sort_values(ascending=False).head(top)
        li = list(value.to_dict().keys())
        li = [str(i) for i in li]
        return li

    #将选出的机构存入best_broker表中，date为存入日期，reason为存入理由
    @gf.typeassert(li=list, date=str, reason=(str, type(None)))
    def list_toSql(self, li, date, reason=None):
        for broker_code in li:
            if gf.isBroker(broker_code):              #在broker_info中找到对应的机构代码
                broker_name = self._dbObject.fetchone(table="broker_info",field="broker_name",
                                                      where="broker_code='%s'"%broker_code)

                #去best_broker中去找是否已有重复数据（同一个日期只有一个机构）
                result = self._dbObject.fetchall(table="best_broker",
                                                 where="broker_code='%s' and date='%s'"%(broker_code,date))
                if len(result) == 0:
                    self._dbObject.insert(table="best_broker", broker_code=broker_code, broker_name=broker_name,
                                          date=date, reason=reason)
                else:
                    print("库中已有%s机构%s数据"%(broker_code,date))
            else:
                print("机构代码不合法，请清洗机构数据")
        print("finished")