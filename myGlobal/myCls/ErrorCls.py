#!/bin/usr/env python
# -*-coding:utf8 -*-
from myGlobal.myCls.msql import DBHelper


#自定义错误类，处理其余类可能出现的错误
class StockError(object):
    def __init__(self, code, ts_date, msg='error'):
        self._code = code
        self._ts_date = ts_date
        self._msg = msg

    @property
    def code(self):
        if self._code == 'code_error':
            return 'code_error'
        else:
            return self._code

    @property
    def ts_date(self):
        if self._ts_date == 'date_error':
            return 'date_error'
        else:
            return self._ts_date

    @property
    def name(self):
        sql = f'select stockname from stock_basic_table where stockcode="{self._code}"'
        t = DBHelper().fetchone(sql)
        if t is not None:
            return t[0]
        else:
            return 'No_Name'

    @property
    def open_price(self):
        return 0.00

    @property
    def close_price(self):
        return 0.00

    @property
    def high_price(self):
        return 0.00

    @property
    def low_price(self):
        return 0.00

    @property
    def volume(self):
        return 0.00

    def next_some_days(self,startdate,days=7):
        li = []
        for i in range(days):
            li.append(StockError('code_error', 'date_error'))
        return li

