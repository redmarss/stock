#!/usr/bin/env python
# -*- coding:utf8 -*-
import myGlobal.globalFunction as gf
import json
from urllib.request import urlopen, Request
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import pymysql
import time
import myGlobal.myCls.msql as msql

list_fq = ['no', 'front', 'back']
stock_list = gf.getAllStock()           #获取所有股票列表


def _getDayData(fqtype, stock_code_list, startdate, filetype, count): #fqtype作为多线程参数一定要放第一个
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd='redmarss', db='tushare',
                                   charset='utf8')
    cur = conn.cursor()
    for _ in range(3):          #循环3次
        for stock_code in stock_code_list:
            url = "https://gupiao.baidu.com/api/stocks/stockdaybar?from=pc&os_ver=1&cuid=xxx&vv=100&format=%s&stock_code=%s&step=3&start=%s&count=%s&fq_type=%s" \
                  % (filetype,stock_code,startdate,count,fqtype)
            try:
                request =Request(url)
                lines = urlopen(request,timeout=10).read()
            except Exception as e:
                print(e)
            else:
                t = json.loads(lines)
                t['stock_code'] = stock_code
                rbyte = json.dumps(t).encode()
            urlPost = "http://localhost:8080/stock/detail/%s" % fqtype
            gf.postData(rbyte,urlPost,stock_code)
            sql = "update stock_basic_table set flag='1' where stockcode='%s'" % stock_code
            cur.execute(sql)
            conn.commit()

    cur.close()

            #dbObject.update(table="stock_basic_table", where='stockcode="%s"' % stock_code, flag='1')


def RunGetDayData():
    mapfunc = partial(_getDayData,stock_code_list=stock_list,startdate='20190101',filetype='json',count='30')
    pool = ThreadPool(3)        #3个线程分别对应front,back,no
    pool.map(mapfunc,list_fq)
    pool.close()
    pool.join()


if __name__ == '__main__':
    RunGetDayData()