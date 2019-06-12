#!/bin/usr/env python
# -*-coding:utf8 -*-


#自定义错误类，处理其余类可能出现的错误
class StockError(object):
    def __init__(self, msg):
        self.__msg = msg
        print(msg)

    @property
    def code(self):
        pass

    @property
    def ts_date(self):
        pass

    @property
    def name(self):
        pass

    @property
    def open_price(self):
        pass

    @property
    def close_price(self):
        pass

    @property
    def high_price(self):
        pass

    @property
    def low_price(self):
        pass

    @property
    def volume(self):
        pass



