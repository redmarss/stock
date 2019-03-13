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
st_list = gf.getAllStock()           #获取所有股票列表


def _getDayData(fqtype, stock_code_list, date, filetype, count): #fqtype作为多线程参数一定要放第一个
    '''
    获取股票日线数据及技术指标，分别存入对应的三张表中
    :param fqtype: 复权参数【'no','front','back'】
    :param stock_code_list: 所要操作的股票代码列表
    :param date: 取该日期前的数据
    :param filetype: 可导出json,csv格式
    :param count: 获取数据天数
    :return:
    '''
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='redmarss', db='tushare',
                                   charset='utf8')
    cur = conn.cursor()
    for _ in range(3):          #为防止网络lag，循环3次
        for stock_code in stock_code_list:
            url = "https://gupiao.baidu.com/api/stocks/stockdaybar?from=pc&os_ver=1&cuid=xxx&vv=100&format=%s&stock_code=%s&step=3&start=%s&count=%s&fq_type=%s" \
                  % (filetype,stock_code,date,count,fqtype)
            try:
                request = Request(url)
                lines = urlopen(request, timeout=10).read()
            except Exception as e:
                print(e)
            else:
                t = json.loads(lines)
                t['stock_code'] = stock_code
                rbyte = json.dumps(t).encode()
            urlPost = "http://localhost:8080/stock/detail/%s" % fqtype
            gf.postData(rbyte,urlPost,flag="daily")
            sql = "update stock_basic_table set %s_flag='1' where stockcode='%s'" % (fqtype, stock_code)
            print("股票代码(%s)%s复权数据完成" % (stock_code,fqtype))
            cur.execute(sql)
            conn.commit()
    cur.close()



def RunGetDayData(stock_list,date,filetype,count):
    '''
    :return:
    '''
    mapfunc = partial(_getDayData,stock_code_list=stock_list,date=date,filetype=filetype,count=count)
    pool = ThreadPool(3)        #3个线程分别对应front,back,no
    pool.map(mapfunc,list_fq)       #会将list_fq参数放在_getDayData参数拦最左边
    pool.close()                    #关闭进程池，不再接受新的进程
    pool.join()                     #主进程阻塞等待子进程的退出


if __name__ == '__main__':
    RunGetDayData(st_list,"20190101","json","30")