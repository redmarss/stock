#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.StockCls

#stockPrice类
#输入一个长度为8的元组作为参数，只读。参数分别是index,stock_code,tsdate,open,close,high,low,volumne
#参数从globalFunction.getStockPrice取
class StockPrice(StockCls):
    __stocktuple = None

    def __init__(self,list1):
        if list(map(lambda x:isinstance(x,StockPriceCls.StockPrice), list1)).count(True) == len(list1):       #判断是否list1中每个元素都是StockPrice类
            print(True)
        else:
            print(False)

    # 初始化
    def __init__(self, tuple):
        if len(tuple) == 8:
            self.__stocktuple = tuple
        else:
            print("StockPrice类参数输入错误")
            return

    @property
    def stock_code(self):
        return self.__stocktuple[1]

    @property
    def ts_date(self):
        return self.__stocktuple[2]

    @property
    def open(self):
        return self.__stocktuple[3]

    @property
    def close(self):
        return self.__stocktuple[4]

    @property
    def high(self):
        return self.__stocktuple[5]

    @property
    def low(self):
        return self.__stocktuple[6]

    @property
    def volumne(self):
        return self.__stocktuple[7]
