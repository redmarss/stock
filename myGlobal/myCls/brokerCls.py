#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.mysqlCls as msql

class Broker(object):
    def __init__(self,code):
        dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', charset='utf8',db='tushare', mycursor='list')
        t = dbObject.fetchone(table='broker_info', field='broker_code,broker_name', where="broker_code='%s'"%code)
        if t is not None:
            self._brokercode = t[0]
            self._brokername = t[1]
        else:
            print("找不到此机构代码")

    @property
    def broker_code(self):
        return self._brokercode

    @property
    def broker_name(self):
        return self._brokername




