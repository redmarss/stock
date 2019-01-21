#!/bin/usr/env python
# -*- coding:utf-8 -*-

import datetime
import time
import myGlobal.globalFunction as gf

def today():
    day = datetime.datetime.today().date()
    return str(day)

@gf.typeassert(strdate=(str,type(None)))
def get_year(strdate = None):
    if strdate is None:
        strdate = today()
    year = datetime.datetime.strptime(strdate, "%Y-%m-%d").year
    return int(year)

@gf.typeassert(strdate=(str,type(None)))
def get_month(strdate = None):
    if strdate is None:
        strdate = today()
    month = datetime.datetime.strptime(strdate, "%Y-%m-%d").month
    return int(month)

#获取"日"
@gf.typeassert(strdate=(str,type(None)))
def get_day(strdate = None):
    if strdate is None:
        strdate = today()
    day = datetime.datetime.strptime(strdate, "%Y-%m-%d").day
    return day

def get_hour():
    return int(datetime.datetime.today().hour)

