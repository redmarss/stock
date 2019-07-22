#!/bin/usr/env python
# -*-coding:utf-8 -*-
from urllib.request import urlopen,Request
from bs4 import BeautifulSoup


url = "http://quote.eastmoney.com/sh600009.html"
user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
referer='http://www.xxxxxx.com/'
headers={'User-Agent':user_agent,'Referer':referer}
request = Request(url,headers=headers)
response =  urlopen(request)
page = response.read().decode('gbk')
soup = BeautifulSoup(page, 'html5lib')

print(page)
flag = soup.findAll('span',{'class':['red wz']})  # 取网页上的股票名称


print(flag)

