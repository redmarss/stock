#!/bin/usr/env python
# -*-coding:utf-8 -*-

from urllib.request import urlopen,Request
from bs4 import BeautifulSoup
import myGlobal.myCls.mysqlCls as msql
import datetime
import myGlobal.globalFunction as gf
import myGlobal.myCls.myException as mexception


#将股票代码及名称写入数据库(每月运行）
def getAllStock():
    url = "http://quote.eastmoney.com/stocklist.html"
    page = urlopen(url).read().decode('gbk')
    soup = BeautifulSoup(page, 'html5lib')
    links = soup.findAll('a')
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss',
                                   db='tushare', charset='utf8')
    for link in links:
        if link.text.find('(') > 0:
            pos = link.text.find('(')
            stockName = link.text[:pos]
            stockCode = link.text[pos+1:-1]
            if stockCode.startswith('30') or stockCode.startswith('60') or stockCode.startswith('00'):
                #写入数据库
                read_sql = dbObject.fetchone(field='stockname', table='stock_basic_table', where='stockcode="%s"'%stockCode)
                if read_sql is None:
                    dbObject.insert(table='stock_basic_table', stockcode=stockCode, stockname=stockName)
                else:
                    dbObject.update(table='stock_basic_table', where='stockcode="%s"'%stockCode,stockname=stockName)
                    # if getStauts(stockCode) == False:
                    #     dbObject.update(table='stock_basic_table', where='stockcode="%s"'%stockCode,status='已退市')


#判断股票是否退市（每判断一次都要访问一个网页，效率有点低）
def getStauts(code):
    url="http://quote.eastmoney.com/"
    if code.startswith('6'):
        url += 'sh%s.html'%code
    elif code.startswith('30') or code.startswith('00'):
        url += 'sz%s.html'%code
    page = urlopen(url).read().decode('gbk')
    soup = BeautifulSoup(page, 'html5lib')
    status = soup.find(id='price9')
    if 'data-bind' in status.attrs.keys():      #status有'data-bind'字段说明未退市，否则为已退市或停牌
        return True
    else:
        return False

#将机构代码、机构名称写入broker_info表（每月运行）
def getBrokerInfo():
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss',
                                   db='tushare', charset='utf8',mycursor='list')
    list_broker = dbObject.fetchall(table='broker_buy_summary', field='broker_code,broker_name')
    list_broker = list(set(list_broker))

    for i in range(len(list_broker)):
        broker_code = list_broker[i][0]
        broker_name = list_broker[i][1]
        getcode = dbObject.fetchone(table='broker_info',where="broker_code='%s'"%broker_code)
        if getcode is None:
            dbObject.insert(table='broker_info',broker_code=broker_code,broker_name=broker_name)
        else:
            dbObject.update(table='broker_info',where="broker_code='%s'"%broker_code,broker_name=broker_name)


#判断是否交易日，并写入数据库
def is_holiday(startdate='2017-01-01'):
    date = datetime.datetime.strptime(startdate, "%Y-%m-%d").date()
    while date<=datetime.date(2018,12,31):
        isholiday = 3

        apiUrl = "http://api.goseek.cn/Tools/holiday?date=" + str(date)
        request = Request(apiUrl)
        try:
            response = urlopen(request)
        except:
            mexception.RaiseError(mexception.dateError)
        else:
            response_data = response.read()
        if str(response_data)[-3] == '0':
            isholiday = 0   # 工作日返回0
        else:
            isholiday = 1   # 节假日返回1

        dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss',
                                       db='tushare', charset='utf8')
        try:
            if not dbObject.fetchone(table="is_holiday",field=date,where="date='%s'"%str(date)):
                dbObject.insert(table="is_holiday",date=str(date),isholiday=str(isholiday))
        except:
            mexception.RaiseError(mexception.sqlError)
        date = date + datetime.timedelta(days=1)


is_holiday()