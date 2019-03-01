import numpy as np
import myGlobal.myCls.msql as msql
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool
from urllib.request import urlopen, Request
import json


# url = "https://gupiao.baidu.com/api/stocks/stockdaybar?from=pc&os_ver=1&cuid=xxx&vv=100&format=json&stock_code=sh600500&step=3&start=20170105&count=160&fq_type=no"
#
# try:
#     request = Request(url)
#     lines = urlopen(request, timeout=10).read()
# except Exception as e:
#     print(e)
#
# t = json.loads(lines)
# t['stock_code']="600000"
# l = json.dumps(t).encode()
# print(l)


url = "http://datainterface3.eastmoney.com/EM_DataCenter_V3/Api//LHBYYBSBCS/GetLHBYYBSBCS?tkn=eastmoney&mkt=&dateNum=&startDateTime=2019-02-18&endDateTime=2019-02-18&sortRule=1&sortColumn=JmMoney&pageNum=1&pageSize=200000&cfg=lhbyybsbcs"

try:
    request = Request(url)
    lines = urlopen(request,timeout=10).read()
except Exception as e:
    print(e)

d = json.loads(lines)
print(len(d['Data'][0]['Data']))