#!/bin/usr/env python
# -*- coding:utf-8 -*-

import datetime
import time
import myGlobal.globalFunction as gf

@gf.typeassert(strdate=str)
def isDate(strdate):
    try:
        date = datetime.datetime.strptime(strdate,"%Y-%m-%d")
        return True
    except:
        return False

@gf.typeassert(strdate=str)
def strTodate(strdate):
    try:
        date = datetime.datetime.strptime(strdate,"%Y-%m-%d").date()
        return date
    except:
        return None

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



@gf.typeassert(str,int)
def diffDay(strdate,day=0):
    '''
    输入一个日期及天数，返回该日期加上/减去该数量的交易日的结果
    :param strdate: 起始日期（必须为交易日）
    :param day: 加上、减去的天数，可以为负
    :return: 返回交易日(str)
    '''
    if gf.is_holiday(strdate) == False:
        date = datetime.datetime.strptime(strdate, "%Y-%m-%d").date()
        if day > 0:
            while day > 0:
                date = date+datetime.timedelta(days=1)
                if not gf.is_holiday(str(date)):                #若非交易日，则不扣除天数
                    day = day-1
        else:
            while day < 0:
                date = date+datetime.timedelta(days=-1)
                if not gf.is_holiday(str(date)):
                    day = day+1
        return str(date)
    else:
        print("diffDay函数所输入的日期非交易日，请修改")
        return None
