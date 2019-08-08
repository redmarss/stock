#!/bin/usr/env python
# -*-coding:utf-8 -*-
from urllib.request import urlopen,Request
from bs4 import BeautifulSoup

import myGlobal.globalFunction as gf
from myGlobal.myCls.Stock import Stock

s = Stock('000915','2018-06-22')
print(s.code)
print(s.getbuyBroker)
