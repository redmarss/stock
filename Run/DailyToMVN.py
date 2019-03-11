#!/usr/bin/env python
# -*- coding:utf8 -*-
import sys
#ABSPATH = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))         #将本文件路径加入包搜索范围
#sys.path.append("H:\\github\\tushareB\\")
import datetime
import time
import myGlobal.globalFunction as gf
import myGlobal.myCls.msql as msql
from urllib.request import urlopen, Request
import json
import re
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial

list_fq = ['no', 'front', 'back']




def _getDayData(stock_code, stardate, filetype, count, fq):
    for _ in range(3):
        url = "https://gupiao.baidu.com/api/stocks/stockdaybar?from=pc&os_ver=1&cuid=xxx&vv=100&format=%s&stock_code=%s&step=3&start=%s&count=%s&fq_type=%s" \
              % (filetype,stock_code,stardate,count,fq)
        try:
            request = Request(url)
            lines = urlopen(request, timeout=10).read()
        except Exception as e:
            print(e)
        else:
            t = json.loads(lines)
            t['stock_code'] = stock_code
            rbyte = json.dumps(t).encode()
        return rbyte

def getAllStockData(startdate,filetype='json',count=160):
#将所有股票代码存入一个list
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare',
                                   charset='utf8')
    li =gf.getAllStock()
    for stock in li:
        for fqtype in ['no', 'front', 'back']:
            print("开始写入%s数据"%fqtype)
            urlPost = "http://localhost:8080/stock/detail/%s" % fqtype
            textByte = _getDayData(stock,startdate,filetype,count,fqtype)
            gf.postData(textByte,urlPost,stock)
        dbObject.update(table="stock_basic_table",where='stockcode="%s"'%stock,flag='1')

#根据日期取出机构交易数据并调用postData函数至数据库
def brokerInfo(startDate=None, endDate=None, pagesize=2000):
    urlPost="http://localhost:8080/broker/purchaseSummary"
    LHBYYBSBCS="http://datainterface3.eastmoney.com/EM_DataCenter_V3/Api//LHBYYBSBCS/GetLHBYYBSBCS?tkn=eastmoney&mkt=&dateNum=&startDateTime=%s&endDateTime=%s&sortRule=1&sortColumn=JmMoney&pageNum=1&pageSize=%s&cfg=lhbyybsbcs"
    try:
        request=Request(LHBYYBSBCS%(startDate,endDate,pagesize))
        text=urlopen(request,timeout=10).read()                     #type is byte
        gf.postData(text,urlPost)
    except Exception as e:
        print(e)

#获取所有股票的交易信息
# def getAllStockData(startDate=None, endDate=None):
#     #将所有股票代码存入一个list
#     li = []
#     # 创建数据库对象（单例模式）
#     dbObject = msql.SingletonModel(host='localhost', port='3306',
#                                          user='root', passwd='redmarss',
#                                          charset='utf8', db='tushare')
#     t_stock = dbObject.fetchall(table="stock_basic_table",field="stockcode")
#     for key in t_stock:
#         li.append(key[0])
#
#     urlPost = 'http://localhost:8080/stock/tradeHistory'        #定义post至mvn的地址
#     for i in li:
#         textByte = getDayData(i, startDate, endDate)                 #从网页获取交易信息
#         gf.postData(textByte, urlPost, i)                       #post至mvn





if __name__ == '__main__':
    # getAllStockData("20190306",count=100)
    if datetime.datetime.today().hour > 18:     #运行时间大于18点
        end = str(datetime.datetime.today().date() + datetime.timedelta(days=1))
    else:
        end = str(datetime.datetime.today().date())
    # 将时间范围定义到（两个月前起）
    start = gf.lastTddate(str(datetime.datetime.today().date()-datetime.timedelta(days=30)))

    #将时间范围内的机构买卖信息导入数据库，重复的不导入
    brokerInfo(start,end,200000)

    #将时间范围内所有股票的交易数据导入数据库
    # starttime1=time.time()
    # getAllStockData(start,end)
    # endtime1=time.time()
    # print(endtime1-starttime1)