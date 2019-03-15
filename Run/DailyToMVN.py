#!/usr/bin/env python
# -*- coding:utf8 -*-
import myGlobal.globalFunction as gf
import json
from urllib.request import urlopen, Request
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import pymysql
import datetime
import myGlobal.myCls.msql as msql
import time

# 定义复权3种模式
list_fq = ['no', 'front', 'back']
# 获取所有股票列表
stock_li = gf.getAllStock(where="no_flag=0 or front_flag=0 or back_flag=0")
def _getDayData(stock_code, date, filetype, count, list_fq): #fqtype作为多线程参数一定要放第一个
    '''
    获取股票日线数据及技术指标，分别存入对应的三张表中
    :param fqtype: 复权参数【'no','front','back'】
    :param stock_code_list: 所要操作的股票代码列表
    :param date: 取该日期前的数据
    :param filetype: json
    :param count: 获取数据天数
    flag : 0:还未处理数据，1：正常处理数据，2：出错数据
    :return:
    '''
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='redmarss', db='tushare',
                                   charset='utf8')
    cur = conn.cursor()
    for _ in range(3):          #为防止网络lag，循环3次
        for fqtype in list_fq:
            url = "https://gupiao.baidu.com/api/stocks/stockdaybar?from=pc&os_ver=1&cuid=xxx&vv=100&format=%s&stock_code=%s&step=3&start=%s&count=%s&fq_type=%s" \
                  % (filetype,stock_code,date,count,fqtype)
            try:
                request = Request(url)
                lines = urlopen(request, timeout=10).read()
            except Exception as e:
                print(e)
                return
            else:
                if len(lines)<50:
                    print("无法取得%s股票相关数据" % stock_code)
                    sql = "update stock_basic_table set %s_flag='2' where stockcode='%s'" % (fqtype, stock_code)
                    cur.execute(sql)
                    conn.commit()
                    return
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



def RunGetDayData(date,filetype,count,list_fq):
    '''

    :param stock_list:需要运行的股票列表
    :param date:开始日期
    :param filetype:文件格式
    :param count:往前倒数的天数
    :return:
    '''
    mapfunc = partial(_getDayData,date=date,filetype=filetype,count=count,list_fq=list_fq)
    pool = ThreadPool(30)        #3个线程分别对应front,back,no
    pool.map(mapfunc,stock_li)       #会将list_fq参数放在_getDayData参数拦最左边
    pool.close()                    #关闭进程池，不再接受新的进程
    pool.join()                     #主进程阻塞等待子进程的退出


#根据日期取出机构交易数据并调用postData函数至数据库
def brokerInfo(startDate=None, endDate=None, pagesize=200000):
    urlPost="http://localhost:8080/broker/purchaseSummary"
    LHBYYBSBCS="http://datainterface3.eastmoney.com/EM_DataCenter_V3/Api//LHBYYBSBCS/GetLHBYYBSBCS?tkn=eastmoney&mkt=&dateNum=&startDateTime=%s&endDateTime=%s&sortRule=1&sortColumn=JmMoney&pageNum=1&pageSize=%s&cfg=lhbyybsbcs"
    try:
        request=Request(LHBYYBSBCS%(startDate,endDate,pagesize))
        text=urlopen(request, timeout=10).read()                     #type is byte
        gf.postData(text,urlPost)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    if datetime.datetime.today().hour > 18:     #运行时间大于18点
        start = str(datetime.datetime.today().date()-datetime.timedelta(days=7))
        end = str(datetime.datetime.today().date() + datetime.timedelta(days=1))
    else:
        start = str(datetime.datetime.today().date() - datetime.timedelta(days=8))
        end = str(datetime.datetime.today().date())
    # 每日获取股票相关数据
    RunGetDayData("20190101","json","500",list_fq)
    #每日获取机构数据
    #brokerInfo(start,end)