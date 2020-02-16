#!/usr/bin/env/python
# -*- coding:utf-8 -*-
# Author:zwd
# DateTime:2019/8/29-22:51
# Project:stock
# File:DailySimulate

import myGlobal.myTime as mTime
import myGlobal.ftypeOperate as fto
from myGlobal.myCls.msql import DBHelper
import myGlobal.globalFunction as gf
from myGlobal.myCls.SimulateCls import BrokerSimulate
from multiprocessing import Pool
from functools import partial

#根据日期，多线程模拟股票买卖
def DailySimulate(t,ftype,amount,tablename):
    #创建BrokerSimulate类实例
    bs = BrokerSimulate(t[0],t[1],ftype,amount,tablename)
    result = bs.simulateBuy(t[2])
    return result


#计算仍需模拟的条数
def getNotCacuTuple(ftype,strdate):
    #strdate = mTime.
    return_list = []
    sql = '''
    SELECT 
    broker_code, DATE_FORMAT(ts_date,'%Y-%m-%d'), stock_code, simulate_flag
    FROM
    broker_buy_summary AS a
    INNER JOIN
    broker_buy_stock_info AS b ON a.id = b.broker_buy_summary_id
    where simulate_flag!=15
    '''
    tuple_all = DBHelper().fetchall(sql)
    for t in tuple_all:
        if not fto.judgeftype(t[3],ftype,1):           #去除已模拟的
            return_list.append(t)
    return return_list



if __name__ == '__main__':
    typelist = [1]                  #一共有多少种方法


    for ftype in typelist:
        tablename = "simulate_buy_way"+str(typelist)
        cacu_list = getNotCacuTuple(ftype)
        print(len(cacu_list))


        pool = Pool(30)
        pool.map(partial(DailySimulate,ftype=ftype,amount=1000,tablename=tablename),cacu_list)
        pool.close()
        pool.join()