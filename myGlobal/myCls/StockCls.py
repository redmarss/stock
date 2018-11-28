#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.StockPriceCls as StockPriceCls

class Stock(StockPriceCls.StockPrice):
    _listStock = list()



    def __init__(self,list1):
        if list(map(lambda x:isinstance(x,StockPriceCls.StockPrice),list1)).count(True)== len(list1):       #判断是否list1中每个元素都是StockPrice类
            print(True)
        else:
            print(False)


    def MA5(self):
        pass


list1=['str',11]
s=Stock(list1)
input()