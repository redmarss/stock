#!/usr/bin/env/python
# -*- coding:utf-8 -*-
# Author:zwd
# DateTime:2019/8/29-22:51
# Project:stock
# File:DailySimulate

import datetime
import myGlobal.ftypeOperate as fto
from myGlobal.myCls.msql import DBHelper
import myGlobal.globalFunction as gf
from myGlobal.myCls.SimulateCls import BrokerSimulate

#根据日期，多线程模拟股票买卖
def DailySimulate(brokercode,ts_date,stockcode,ftype,amount,tablename):
    #创建BrokerSimulate类实例
    bs = BrokerSimulate(brokercode,ts_date,ftype,amount,tablename)
    result = bs.simulateBuy(stockcode)
    return result


def getNotCacuTuple(ftype):
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
        if not fto.judgeftype(t[3],ftype,1):
            return_list.append(t)
    return return_list



if __name__ == '__main__':
    # broker_list = gf.getBroker()            #获取所有列表
    # startdate = datetime.datetime.strptime('2017-01-01',"%Y-%m-%d").date()
    # enddate = datetime.datetime.today().date()
    #
    # print(broker_list)
    # for brokercode in broker_list:
    #     simudate = startdate
    #     while simudate < enddate:
    #         DailySimulate(brokercode,str(simudate),1,1000,"simulate_buy")
    #         print(f"计算{brokercode}于{simudate}的交易")
    #         simudate = simudate + datetime.timedelta(days=1)

    ftype = 1
    cacu_list = getNotCacuTuple(ftype)                  #第一种方式
    print(len(cacu_list))
    for t in cacu_list:
        DailySimulate(t[0],t[1],t[2],ftype,1000,"simulate_buy")
