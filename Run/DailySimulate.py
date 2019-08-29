#!/usr/bin/env/python
# -*- coding:utf-8 -*-
# Author:zwd
# DateTime:2019/8/29-22:51
# Project:stock
# File:DailySimulate

import datetime
import time
import myGlobal.globalFunction as gf
from myGlobal.myCls.SimulateCls import BrokerSimulate

#根据日期，多线程模拟股票买卖
def DailySimulate(brokercode,ts_date,ftype,amount,tablename):
    #创建BrokerSimulate类实例
    bs = BrokerSimulate(brokercode,ts_date,ftype,amount,tablename)
    result = bs.simulateBuy()
    return result


if __name__ == '__main__':
    broker_list = gf.getBroker()            #获取所有列表
    startdate = datetime.datetime.strptime('2017-01-01',"%Y-%m-%d").date()
    enddate = datetime.datetime.today().date()

    print(broker_list)
    for brokercode in broker_list:
        simudate = startdate
        while simudate < enddate:
            DailySimulate(brokercode,str(simudate),1,1000,"simulate_buy")
            simudate = simudate + datetime.timedelta(days=1)