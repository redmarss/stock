#!/usr/bin/env/python
# -*- coding:utf-8 -*-
# Author:zwd
# DateTime:2019/9/22-13:59
# Project:stock
# File:BrokerAnalyzeCls

from myGlobal.myCls.msql import DBHelper
import pandas as pd

class BrokerAnalyze(object):
    def __init__(self,brokercode, enddate, ftype):
        self._brokercode = brokercode
        self._enddate = enddate
        self._ftype = ftype

    def getHisTradeResult(self):
        #自定义查询语句字段
        field_list = ['broker_code','stock_code','ts_date','buy_date','sell_date','gainmoney','gainpercent','ftype']
        field = ""
        for i in field_list:
            field += f"{i},"
        field = field.rstrip(",")

        sql = f'''select {field} from simulate_buy 
        where broker_code='{self._brokercode}' and ts_date<='{self._enddate}' and ftype={self._ftype}'''
        t = DBHelper().fetchall(sql)
        df = pd.DataFrame(list(t))
        return df


if __name__ == '__main__':
    ba = BrokerAnalyze('80065939','2019-09-20','1')
    ba.getHisTradeResult()

