#!/usr/bin/env python
# -*- coding:utf-8 -*-
import myGlobal.globalFunction as gf
import myGlobal.myCls.mysqlCls as msql
import pandas as pd


class AnalyzeBroker(object):
    #构造函数
    @gf.typeassert(startdate=str, enddate=str, recorddate=str, reason=str)
    def __init__(self, startdate, enddate, recorddate, reason):
        self.startdate = startdate
        self.enddate = enddate
        self.recorddate = recorddate
        self.reason = reason
        self.dbObject = msql.SingletonModel(host="localhost",port="3306",user="root",passwd="redmarss",db="tushare",charset="utf8")

    #通过平均值方式选取机构，count为时间段内交易次数，top为选前几名
    @gf.typeassert(count=int, top=int)
    def getTopBroker_avr(self,count=5, top=30, simulatetable="simulate_buy"):
        '''
        根据平均值的算法得出最好的机构
        :param count: 在时间范围内的交易次数（int类型）
        :param top: 前几个机构
        :param table: 默认为simulate_buy表
        :return: list[]  broker_code的集合
        '''
        field_list = ["ts_date","broker_code","stock_code","buy_price","sell_price","amount","gainmoney","gainpercent"]
        field = ""
        for i in field_list:
            field += "%s," % i
        field = field.rstrip(",")
        t = self.dbObject.fetchall(table=simulatetable, field=field,
                                    where="ts_date between '%s' and '%s'" % (self.startdate, self.enddate))
        if len(t) == 0:
            print("%s表中没有模拟数据，找不到相关机构" % simulatetable)
            return
        df = pd.DataFrame(list(t), columns=field_list)
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
    @gf.typeassert(li=list, table=str)
    def list_toSql(self, li,table="best_broker"):
        for broker_code in li:
            if gf.isBroker(broker_code):              #在broker_info中找到对应的机构代码
                broker_name = self.dbObject.fetchone(table="broker_info", field="broker_name",
                                                     where="broker_code='%s'" % broker_code)

                #去best_broker中去找是否已有重复数据（同一个日期只有一个机构）
                result = self.dbObject.fetchall(table=table,
                                                where="broker_code='%s' and date='%s' and reason='%s'"
                                                      % (broker_code, self.recorddate, self.reason))
                if len(result) == 0:
                    self.dbObject.insert(table=table, broker_code=broker_code, broker_name=broker_name,
                                         date=self.recorddate, reason=self.reason)
                else:
                    print("库中已有%s机构%s数据" % (broker_code, self.recorddate))
            else:
                print("机构代码不合法，请清洗机构数据")
        print("finished")

# if __name__ == "__main__":
#     analyzeBroker = AnalyzeBroker("2017-02-01", "2017-03-01")
#     print(analyzeBroker.getTopBroker_avr())