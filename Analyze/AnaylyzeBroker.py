#!/bin/usr/env python
# -*- coding:utf-8 -*-

# AnalyzeBroker(tablename,startdate,enddate)
#
# (simulate_buy)(已在Broker类中实现)取得所有机构名称，模拟买入（第二天买，第三天卖），存入everydaysimulatebuy
#按照不同时间段（date）选出一定数量(top)的机构,存入数据库
#按照不同数据库中的机构进行模拟买入，并统计盈利


#NOET:1.删除best_broker，重新生成best_broker。2.跑数据，导出所有数据至U盘
#每月10日跑上一月数据
import myGlobal.myCls.mysqlCls as msql
import myGlobal.myCls.StockCls as mstock
import myGlobal.globalFunction as gf
import datetime
import Run.DailyRun as dr
import pandas as pd




def CacuBroker(strstart,strend):
    try:
        startdate = datetime.datetime.strptime(strstart,"%Y-%m-%d").date()
        enddate = datetime.datetime.strptime(strend,"%Y-%m-%d").date()
    except:
        print("日期输入错误")
        return
    date = startdate
    while date < enddate:
        start = datetime.date(date.year,date.month-1,1)             #获得上月1日
        end = datetime.date(date.year,date.month,1)-datetime.timedelta(days=1)      #获得上月最后一天

        bs = BrokerSimulate(str(start),str(end),str(end),str(end))
        li = bs.getTopBroker_avr(3,20)
        bs.list_toSql(li,str(end))
        bs.everyday_stock_record()
        date = date+datetime.timedelta(days=1)

def AnaylyzeHistory(start,end):
date=datetime.datetime.strptime(start,"%Y-%m-%d").date()
while date <= datetime.datetime.strptime(end,"%Y-%m-%d").date():

    date = date+datetime.timedelta(days=1)


# def everyday_stock_record(startdate="2017-02-01",enddate="2018-12-20"):
#     if isinstance(startdate,str):
#         startdate = datetime.datetime.strptime(startdate,"%Y-%m-%d").date()
#     if isinstance(enddate,str):
#         enddate = datetime.datetime.strptime(enddate,"%Y-%m-%d").date()
#     date = startdate
#     while date<=enddate:
#         if gf.is_holiday(str(date)) == False:
#             #计算当天股票
#             li_stock = dr.getStockEveryDay(str(date))
#             #存入数据库
#             if len(li_stock) >0:
#                 for stock in li_stock:
#                     _everyday_stock_simulate_buy(date,stock,1000)
#         date = date + datetime.timedelta(days=1)

# def To_sql(li,reason=None):
#     dbObject = msql.SingletonModel(host="localhost", port="3306", user="root", passwd="redmarss", db="tushare",
#                                    charset="utf8")
#     li = map(lambda x: str(x), li)
#     for broker_code in li:
#         if gf.isBroker(broker_code):  # 在broker_info中找到对应的机构代码
#
#             broker_name = dbObject.fetchone(table="broker_info", field="broker_name",
#                                                   where="broker_code='%s'" % broker_code)[0]
#
#             # 去best_broker中去找是否已有重复数据
#             result = dbObject.fetchall(table="best_broker_list",
#                                              where="broker_code='%s'" % broker_code)
#             if len(result) == 0:
#                 dbObject.insert(table="best_broker_list", broker_code=broker_code, broker_name=broker_name,
#                                       reason=reason)
#             else:
#                 pass
#                 #print("库中已有%s机构%s数据" % (broker_code, date))
#     print("finished")

if __name__  == '__main__':
    CacuBroker("2017-02-01","2017-05-01")
    # li=getTopBroker_avr(3,20,"2019-01-01")
    # list_to_bestbrokerlist(li)
    # everyday_stock_record("2017-01-01","2019-01-31")


