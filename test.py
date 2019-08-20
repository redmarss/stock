#!/bin/usr/env python
# -*-coding:utf-8 -*-

import myGlobal.globalFunction as gf
from myGlobal.myCls.Stock import Stock



class Stock(object):

    def __init__(self,stockcode,ts_date):
        self._stockcode=stockcode
        self._ts_date = ts_date
        print("Stock"+self._stockcode+self._ts_date)

class Broker(object):
    def __init__(self,broker_code,ts_date):
        self._brokercode=broker_code
        self._ts_date = ts_date
        print("Broker"+self._brokercode+self._ts_date)

class Simulate(Stock,Broker):
    def __init__(self,stockcode,brokercode,ts_date,ftype):
        Broker.__init__(self,brokercode,ts_date)
        Stock.__init__(self,stockcode,ts_date)
        self._ftype= ftype
        print(self._brokercode)
        print(self._ftype)



if __name__ == '__main__':
    Simulate("600000","80010101","2017-03-16",1)
