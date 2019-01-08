#!/usr/bin/env python
# -*- coding:utf8 -*-
import sys
#ABSPATH = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))         #将本文件路径加入包搜索范围
sys.path.append("H:\\github\\tushareB\\")
import datetime
import myGlobal.globalFunction as gf
import myGlobal.myCls.mysqlCls as msql
from urllib.request import urlopen, Request
import re
# import tushare as ts
# import time
# import json
# from tushare.stock import ref_vars as rv

#获取股票日线数据
def getDayData(code=None,start="2017-01-01",end="2018-12-31"):
    symbol = gf._code_to_symbol(code)       #将代码转换成标准格式
    if gf.isStockA(symbol):
        url = 'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq2017&param=%s,day,%s,%s,640,qfq'%(symbol,start,end)
        try:
            request=Request(url)
            lines=urlopen(request,timeout=10).read()
            if len(lines)<100:  #no data
                return None
        except Exception as e:
            print(e)
        else:
            lines=lines.decode('utf-8')
            lines = lines.split('=')[1]
            reg = re.compile(r',{"nd.*?}')
            lines = re.subn(reg, '', lines)
            reg=re.compile(r',"qt":{.*?}')
            lines = re.subn(reg, '', lines[0])
            reg=r',"mx_price".*?"version":"4"'
            lines = re.subn(reg, '', lines[0])
            reg=r',"mx_price".*?"version":"12"'
            lines = re.subn(reg, '', lines[0])
            #将str格式转换成byte
            textByte=bytes(lines[0],encoding='utf-8')
        return textByte

#根据日期取出机构交易数据并调用postData函数至数据库
def brokerInfo(startDate=None, endDate=None, pagesize=2000):
    urlPost="http://localhost:8080/broker/purchaseSummary"
    LHBYYBSBCS="http://datainterface3.eastmoney.com/EM_DataCenter_V3/Api//LHBYYBSBCS/GetLHBYYBSBCS?tkn=eastmoney&mkt=&dateNum=&startDateTime=%s&endDateTime=%s&sortRule=1&sortColumn=JmMoney&pageNum=1&pageSize=%s&cfg=lhbyybsbcs"
    try:
        request=Request(LHBYYBSBCS%(startDate,endDate,pagesize))
        text=urlopen(request,timeout=10).read()                     #type is byte
        print(text)
        gf.postData(text,urlPost)
    except Exception as e:
        print(e)

#获取所有股票的交易信息
def getAllStockData(startDate=None, endDate=None):
    #将所有股票代码存入一个list
    li = []
    # 创建数据库对象（单例模式）
    dbObject = msql.SingletonModel(host='localhost', port='3306',
                                         user='root', passwd='redmarss',
                                         charset='utf8', db='tushare')
    t_stock = dbObject.fetchall(table="stock_basic_table",field="stockcode")
    for key in t_stock:
        li.append(key[0])

    urlPost = 'http://localhost:8080/stock/tradeHistory'        #定义post至mvn的地址
    for i in li:
        textByte = getDayData(i, startDate, endDate)                 #从网页获取交易信息
        gf.postData(textByte, urlPost, i)                       #post至mvn


if __name__ == '__main__':
    # 将时间范围定义到（今天至14天前）
    start=gf.lastTddate(str(datetime.datetime.today().date()-datetime.timedelta(days=14)))
    end=str(datetime.datetime.today().date())
    #将时间范围内的机构买卖信息导入数据库，重复的不导入
    brokerInfo(start,end,200000)

    #将时间范围内所有股票的交易数据导入数据库
    getAllStockData(start,end)