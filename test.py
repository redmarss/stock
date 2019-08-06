#!/bin/usr/env python
# -*-coding:utf-8 -*-
from urllib.request import urlopen,Request
from bs4 import BeautifulSoup

import myGlobal.globalFunction as gf

#code = ["sz600000","600000","600000.sz","600000sz"]
code = ["sz6000001","60000000","60000000.sz","6000000sz"]

for i in code:
    code_output= gf.code_to_symbol(i)
    print(code_output)
