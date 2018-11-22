#!/bin/usr/env python
# -*-coding:utf-8 -*-

from urllib.request import urlopen,Request
from bs4 import BeautifulSoup
import myGlobal.mysqlCls as msql
import pandas as pd

def getAllStock():
    url = "http://quote.eastmoney.com/stocklist.html"
    page = urlopen(url).read().decode('gbk')
    soup = BeautifulSoup(page, 'html5lib')
    links = soup.findAll('a')
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='test', charset='utf8')
    dfStock = pd.DataFrame()
    for link in links:
        if link.text.find('(') > 0:
            pos = link.text.find('(')
            stockName = link.text[:pos]
            stockCode = link.text[pos+1:-1]
            if stockCode.startswith('30') or stockCode.startswith('60') or stockCode.startswith('00'):
                #写入dfStock
                df_insert = pd.DataFrame({'code':stockCode, 'name':stockName}, index=[0])
                dfStock = dfStock.append(df_insert)
    dfStock.set_index('code')

    dbObject.DataframeToSql(dfStock,'stockTable')


getAllStock()