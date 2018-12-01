#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.mysqlCls as msql
import myGlobal.globalFunction as gf
from pandas import Series

#Stock类
#输入股票代码，日期作为参数
class Stock(object):
    _listDict = dict()
    _ts_date = None
    _code = None

    def __init__(self, code, ts_date):
        self._code = code
        self._ts_date = ts_date
        if not code.lower().startswith('s'):
            code = gf._code_to_symbol(code)

        dbObject = msql.SingletonModel(host='localhost',port='3306',user='root',passwd='redmarss',db='tushare',charset='utf8')
        try:
            self._listDict = dbObject.fetchone(table='stock_trade_history_info', where='stock_code="%s" and ts_date="%s"'%(code,ts_date))
            print(self._listDict)
        except:
            print("code或ts_date有误或不是交易日")
            self._listDict = None

    @property
    def code(self):
        return str(self._code)

    @property
    def ts_date(self):
        return str(self._ts_date)

    @property
    def open_price(self):
        if self._listDict is not None:
            return float(self._listDict['open_price'])

    @property
    def close_price(self):
        if self._listDict is not None:
            return float(self._listDict['close_price'])

    @property
    def high_price(self):
        if self._listDict is not None:
            return float(self._listDict['high_price'])

    @property
    def low_price(self):
        if self._listDict is not None:
            return float(self._listDict['low_price'])

    @property
    def volume(self):
        if self._listDict is not None:
            return float(self._listDict['volume'])


    def MA(self,days=5):
        if self._listDict is None:
            print("%s不是交易日"%self.ts_date)
            return

        list_MA=[]
        t_MA = gf.getStockPrice(self.code,self.ts_date,0-days)
        for i in range(len(t_MA)):
            list_MA.append(t_MA[i]['close_price'])
        s = Series(list_MA)
        return round(s.mean(),2)

s=Stock('600000','2018-01-07')

input()