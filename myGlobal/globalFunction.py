#!/bin/usr/env python
# -*- coding:utf-8 -*-

import myGlobal.mysqlCls as msql
import datetime
import re
import csv
from urllib.request import urlopen,Request

#获取所有股票代码
def getAllStockCode():
    

#判断是否涨停板,若涨停，返回True，否则返回False;含S的股票名称（ST,S）,涨幅为5%
def isLimit(code,openPrice,nowPrice):
    if isinstance(code,str)==False:
        code=str(code)
    if isinstance(openPrice,float)==False:
        open=float(openPrice)
    if isinstance(nowPrice,float)==False:
        price=float(nowPrice)

    name=None
    if code in getAllStockCode().keys():
        name=str(getAllStockCode()[code])
    else:
        print("找不到此代码对应的股票")
        return
    if name.startswith('s') or name.startswith('S'):
        if price == round(1.05*open, 2):
            return True
        else:
            return False
    else:
        if price == round(1.1*open, 2):
            return True
        else:
            return False