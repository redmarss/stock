#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.mysqlCls as msql
from urllib.request import Request,urlopen
import datetime

#获取所有股票代码
def getAllStockCode():
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare', charset='utf8')
    liststcok = dbObject.fetchall(table='stock_basic_table', field='stockcode,stockname')
    return liststcok

#判断是否涨停板,若涨停，返回True，否则返回False;含S的股票名称（ST,S）,涨幅为5%,超出涨幅返回空
def isLimit(code, openPrice, nowPrice):
    if isinstance(code,str)==False:
        code = str(code)
    if isinstance(openPrice,float)==False:
        open = float(openPrice)
    if isinstance(nowPrice,float)==False:
        price = float(nowPrice)

    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare', charset='utf8')
    namedict = dbObject.fetchone(table='stock_basic_table', field='stockname', where='stockcode="%s"'%code)
    if namedict is not None:
        name=str(namedict['stockname'])
    else:
        print("找不到此代码对应的股票")
        return
    if name.upper().find('S')>0:                #名字中包含S，涨幅为5%
        if price == round(1.05*open, 2):
            return True
        elif price>round(1.05*open, 2):
            print("超出每日限制涨幅")
            return
        else:
            return False
    else:
        if price == round(1.1*open, 2):
            return True
        elif price > round(1.1*open, 2):
            print("超出每日限制涨幅")
            return
        else:
            return False


#判断股票涨或跌，涨返回True，跌或平返回False
def RaiseOrFall(open, close):
    if open < close:
        return True
    else:
        return False

#输入三个价格，返回幅度
def ChangeRange(priceLastClose,priceOpen,priceClose):
    '''
        priceLastClose:昨日收盘价（今日开盘基准价）
        priceOpen:今日开盘价
        priceClose：今日收盘价或当前价格
        返回：收盘-开盘的涨幅，保留4位小数
    '''
    range=(priceClose-priceOpen)/priceLastClose
    return round(range,4)

#判断是否为交易日，返回工作日返回False or 节假日返回True
def is_holiday(date):
    '''
            1、接口地址：http://api.goseek.cn/Tools/holiday?date=数字日期，支持https协议。
            2、返回数据：工作日对应结果为 0, 休息日对应结果为 1, 节假日对应的结果为 2
            3、节假日数据说明：本接口包含2017年起的中国法定节假日数据，数据来源国务院发布的公告，每年更新1次，确保数据最新
            4、示例：
            http://api.goseek.cn/Tools/holiday?date=20170528
            https://api.goseek.cn/Tools/holiday?date=20170528
            返回数据：
            {"code":10001,"data":2}

    '''
    if not isinstance(date, str):
        date = str(date)

    apiUrl = "http://api.goseek.cn/Tools/holiday?date="+str(date)
    request = Request(apiUrl)
    try:
        response = urlopen(request)
    except Exception as e:
        print(e)
        print("时间输入有误")
    else:
        response_data = response.read()

    if str(response_data)[-3]=='0':
        return False                    #工作日返回False
    else:
        return True                     #节假日返回True

#返回上一交易日（字符串格式）
def lastTddate(strdate):
    try:
        date = datetime.datetime.strptime(strdate, "%Y-%m-%d").date()
        while is_holiday(str(date))==True:
            date = date-datetime.timedelta(days=1)
        return str(date)
    except:
        print("日期输入有误")

#输入一个日期及天数，返回该日期加上/减去该数量的交易日的结果
def diffDay(strdate,day=0):
    try:
        date = datetime.datetime.strptime(strdate, "%Y-%m-%d").date()
        if day > 0:
            while day > 0:
                date = date+datetime.timedelta(days=1)
                if not is_holiday(date):                #若非休息日，day-1
                    day = day-1
        else:
            while day < 0:
                date = date+datetime.timedelta(days=-1)
                if not is_holiday(date):
                    day = day+1
        return str(date)
    except:
        print("日期或天数输入有误")