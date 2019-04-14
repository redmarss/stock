# -*- coding:utf8  -*-
from myGlobal.myCls.BrokerCls import Broker
from myGlobal.myCls.StockCls import Stock
from myGlobal.myCls.msql import DBHelper
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import myGlobal.myTime as myTime
import datetime

#多线程模拟每日机构买卖股票
def _DailySimulate(brokercode,strdate,tablename,amount,type):
    b = Broker(brokercode,strdate)
    b.simulate(tablename=tablename,ts_date=strdate,amount=amount,ftype=type)

#根据输入日期，找出当日上榜机构
def _getBrokerToday(strdate):
    sql = "select broker_code from broker_buy_summary where b_count>0 and ts_date='%s'" % strdate
    t_broker = DBHelper().fetchall(sql)
    #将机构列表存入list，以便后续计算
    li_broker = []
    for i in range(len(t_broker)):
        if t_broker[i][0] not in li_broker:
            li_broker.append(t_broker[i][0])
    return li_broker

#多线程执行每日模拟计算（方法1+方法2）
def mapDailySimulate(strdate,tablename,amount,type):
    #先根据输入日期找出当日上榜机构,存入list
    li_broker = _getBrokerToday(strdate)
    mapfunc = partial(_DailySimulate,strdate=strdate,tablename=tablename,amount=amount,type=type)
    pool = ThreadPool(10)
    pool.map(mapfunc,li_broker)
    pool.close()
    pool.join()




if __name__ =='__main__':
    startdate = "2017-01-01"
    enddate = "2019-04-01"
    date = myTime.strTodate(startdate)
    while date <= myTime.strTodate(enddate):
        mapDailySimulate(str(date),"simulate_buy",1000,1)
        date = date+datetime.timedelta(days=1)
