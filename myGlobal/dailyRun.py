#!/bin/usr/env python
# -*-coding:utf-8 -*-

from urllib.request import urlopen,Request
from bs4 import BeautifulSoup

def getAllStock():
    url = "http://quote.eastmoney.com/stocklist.html"
    page = urlopen(url).read().decode('gbk')
    soup = BeautifulSoup(page, 'html5lib')
    links = soup.findAll('a')
    for link in links:
        if link.text.find('(') > 0:
            pos = link.text.find('(')
            stockName = link.text[:pos]
            stockCode = link.text[pos+1:-1]
            if stockCode.startswith('300') or stockCode.startswith('600') or stockCode.startswith('002'):
                #插入数据库



getAllStock()