#!/bin/usr/env python
# -*-coding:utf-8 -*-
from urllib.request import urlopen,Request
import dateu as du
import cons as ct
import pandas as pd
from pandas.compat import StringIO
from bs4 import BeautifulSoup

import myGlobal.globalFunction as gf
from myGlobal.myCls.Stock import Stock



get_stock_basics("2019-04-05")