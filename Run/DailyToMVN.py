#!/usr/bin/env python
# -*- coding:utf8 -*-
import myGlobal.globalFunction as gf
import json
from urllib.request import urlopen, Request
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import pymysql
import datetime
import myGlobal.myCls.msql as msql
import time
import re


def _getDayData(code=None,start="2017-01-01",end="2018-12-31"): #code作为多线程参数一定要放第一个
    url = 'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq2017&param=%s,day,%s,%s,640,qfq'\
          %(code,start,end)
    try:
        request = Request(url)
        lines = urlopen(request, timeout=10).read()
        if len(lines) < 100:  # no data
            return None
    except Exception as e:
        print(e)
    else:
        lines = lines.decode('utf-8')
        lines = lines.split('=')[1]
        reg = re.compile(r',{"nd.*?}')
        lines = re.subn(reg, '', lines)
        reg = re.compile(r',"qt":{.*?}')
        lines = re.subn(reg, '', lines[0])
        reg = r',"mx_price".*?"version":"4"'
        lines = re.subn(reg, '', lines[0])
        reg = r',"mx_price".*?"version":"12"'
        lines = re.subn(reg, '', lines[0])
        # 将str格式转换成byte
        textByte = bytes(lines[0], encoding='utf-8')
    urlPost = 'http://localhost:8080/stock/tradeHistory'
    gf.postData(textByte,urlPost,flag='stock')          #flag标记为每日股票数据
    print("%s股票从%s至%s数据导入完成"%(code,start,end))


def RunGetDayData(start="2017-01-01",end="2019-04-01"):
    '''

    :param stock_list:需要运行的股票列表
    :param date:开始日期
    :param filetype:文件格式
    :param count:往前倒数的天数
    :return:
    '''
    stock_li = gf.getAllStock()
    mapfunc = partial(_getDayData,start=start,end=end)
    pool = ThreadPool(10)        #3个线程分别对应front,back,no
    pool.map(mapfunc,stock_li)       #会将list_fq参数放在_getDayData参数拦最左边
    pool.close()                    #关闭进程池，不再接受新的进程
    pool.join()                     #主进程阻塞等待子进程的退出


#根据日期取出机构交易数据并调用postData函数至数据库
def brokerInfo(startDate=None, endDate=None, pagesize=200000):
    urlPost="http://localhost:8080/broker/purchaseSummary"
    LHBYYBSBCS="http://datainterface3.eastmoney.com/EM_DataCenter_V3/Api//LHBYYBSBCS/GetLHBYYBSBCS?tkn=eastmoney&mkt=&dateNum=&startDateTime=%s&endDateTime=%s&sortRule=1&sortColumn=JmMoney&pageNum=1&pageSize=%s&cfg=lhbyybsbcs"
    try:
        request=Request(LHBYYBSBCS%(startDate,endDate,pagesize))
        text=urlopen(request, timeout=10).read()                     #type is byte
        gf.postData(text,urlPost)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    if datetime.datetime.today().hour > 18:     #运行时间大于18点
        start = str(datetime.datetime.today().date()-datetime.timedelta(days=7))
        end = str(datetime.datetime.today().date() + datetime.timedelta(days=1))


    else:
        start = str(datetime.datetime.today().date() - datetime.timedelta(days=8))
        end = str(datetime.datetime.today().date())

    #everyday = start.replace("-","")
    #每日获取股票相关数据
    RunGetDayData(start,end)
    #每日获取机构数据
    brokerInfo(start,end)