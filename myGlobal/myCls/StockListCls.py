#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.StockCls as StockCls

class StockList(object):
    _stocklist = None

    def __init__(self,list1):
        if list(map(lambda x:isinstance(x,StockCls.Stock), list1)).count(True) == len(list1):       #判断是否list1中每个元素都是Stock类
            self._stocklist = list1
        else:
            print("参数列表不全为Stock类，错误")
            return None

