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
    broker_code = t[0]
    ts_date = t[1]
    stock_code = t[2]
    bs = BrokerSimulate(broker_code,ts_date,ftype,amount,tablename)
    result = bs.simulateBuy(stock_code)
    return result


#计算仍需模拟的条数
def getCaclList(ftype,enddate,startdate='2017-01-01'):
    return_list = []
    #找出
    sql = f'''
    SELECT 
    broker_code, DATE_FORMAT(ts_date,'%Y-%m-%d'), stock_code, simulate_flag
    FROM
    broker_buy_summary AS a
    INNER JOIN
    broker_buy_stock_info AS b ON a.id = b.broker_buy_summary_id
    where ts_date between '{startdate}' and '{enddate}'
    '''
    tuple_all = DBHelper().fetchall(sql)
    for t in tuple_all:
        simulate_flage = t[3]
        if not fto.judgeftype(simulate_flage,ftype,1):           #去除已模拟的
            return_list.append(t)
    print(f"{startdate}至{enddate}仍有{len(return_list)}条数据未用方式{ftype}模拟")
    return return_list


#模拟买入hotbar数据
def HotBarSimulate(strdate):
    #找出需模拟的数据条数
    select_sql = f"""
    select * from hotbar where date<='{strdate}' and is_simulate=0
    """
    select_t = DBHelper().fetchall(select_sql)
    #模拟计算
    for t in select_t:      #t like (1, '2020-03-11', '08:30:00', 'sz002503', '搜于特', '0')
        print(t)


if __name__ == '__main__':
    # typelist = [1]                  #将需要模拟的ftype存入这个list
    #
    # #寻找今天前7个交易日，只能模拟<至少>3个交易日前的记录，否则会导致数据不全
    # strToday = mTime.Today()
    # strdate = mTime.diffDay(strToday,-7)
    #
    #
    # for ftype in typelist:
    #     tablename = "simulate_buy_way_"+str(ftype)
    #     cacu_list = getCaclList(ftype,enddate=strdate)     #startdate默认为"2017-01-01"
    #
    #     # for l in cacu_list:
    #     #     DailySimulate(l, ftype=ftype, amount=1000, tablename=tablename)
    #
    #     pool = Pool(30)
    #     pool.map(partial(DailySimulate,ftype=ftype,amount=1000,tablename=tablename),cacu_list)
    #     pool.close()
    #     pool.join()

    #每日模拟买入前3交易日前hotbar数据
    strToday = mTime.Today()
    strdate = mTime.diffDay(strToday,-2)

    HotBarSimulate(strdate)