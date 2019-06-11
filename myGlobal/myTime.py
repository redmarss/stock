#!/bin/usr/env python
# -*- coding:utf-8 -*-

import datetime
import time
import myGlobal.globalFunction as gf
from myGlobal.myCls.msqlHelper import DBHelper

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

def getAllTradeDate(startdate='2017-01-01',enddate='2017-12-31'):
    date_list = []
    try:
        start = datetime.datetime.strptime(startdate,"%Y-%m-%d")
        end = datetime.datetime.strptime(enddate,"%Y-%m-%d")
    except:
        print("输入日期有误")
    if start>end:
        print("开始日期应小于结束日期")
        return
    sql = 'select date from is_holiday where date between "%s" and "%s" and isholiday=0' % (startdate,enddate)
    t = DBHelper().fetchall(sql)
    for i in range(len(t)):
        if t[i][0] not in date_list:
            date_list.append(t[i][0])
    return date_list

