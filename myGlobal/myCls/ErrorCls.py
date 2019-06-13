#!/bin/usr/env python
# -*-coding:utf8 -*-
from myGlobal.myCls.msqlHelper import DBHelper


#自定义错误类，处理其余类可能出现的错误
class StockError(object):
    def __init__(self, code,ts_date,msg):
        self._code = code
        self._tsdate = ts_date
        self._msg = msg

    @property
    def code(self):
        return self._code

    @property
    def ts_date(self):
        return self._ts_date

    @property
    def name(self):
        sql = f'select stockname from stock_basic_table where stockcode="{self._code}"'
        t = DBHelper().fetchone(sql)[0]
        return t

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



