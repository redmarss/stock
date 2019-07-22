#!/bin/usr/env python
# -*-coding:utf-8 -*-
from urllib.request import urlopen,Request
from bs4 import BeautifulSoup


url = "http://quote.eastmoney.com/sh600002.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/58.0.3029.110 Safari/537.36",
    }


request = Request(url,headers=headers)
response =  urlopen(request)
page = response.read().decode('gbk')
soup = BeautifulSoup(page, 'html5lib')

print(page)
flag = soup.findAll('span',{'class':['red wz']})  # 取网页上的股票名称


print(flag)

