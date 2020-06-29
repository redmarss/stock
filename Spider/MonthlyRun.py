#!/bin/usr/env python
# -*-coding:utf-8 -*-
import sys
sys.path.append("H:\\python\\stock\\")

from urllib.request import urlopen,Request
from urllib.error import HTTPError
import requests
from bs4 import BeautifulSoup

import myGlobal.globalFunction as gf
import myGlobal.myTime as myTime
from myGlobal.myCls.msql import DBHelper
from myGlobal.myCls.multiProcess import threads
import myGlobal.myCls.msql as msql
import datetime

import pymysql
import pandas as pd
from pandas.compat import StringIO


def _updateBasicTableInfo(code,t):
    tablename = "stock_basic_table"
    t_sql = f"select * from {tablename} where stockcode='{code}'"
    t_result = DBHelper().fetchall(t_sql)          #查出数据库中股票代码为code的条数（一般为0或1）
    field = '''(stockcode,stockname,industry,area,pe,outstanding,totals,totalAssets,liquidAssets,fixedAssets,
            reserved,reservedPe,esp,bvps,pb,timeToMarket,undp,perundp,rev,profit,gpr,npr,holders)'''

    if len(t_result) == 0:                              #数据库中不存在股票代码为code的记录
        #插入数据
        DBHelper().insertTupleToTable(tablename,t,field)
        print(f"插入{code}信息成功")
    elif len(t_result) == 1:
        #更新数据
        update_sql = f"delete from {tablename} where stockcode='{code}'"
        DBHelper().execute(update_sql)
        DBHelper().insertTupleToTable(tablename,t,field)
        print(f"更新{code}信息成功")


def getAllStock():
    """
        获取沪深上市公司基本情况
    Parameters
    date:日期YYYY-MM-DD，默认为上一个交易日，目前只能提供2016-08-09之后的历史数据

    Return
    --------
    DataFrame
               code,代码
               name,名称
               industry,细分行业
               area,地区
               pe,市盈率
               outstanding,流通股本
               totals,总股本(万)
               totalAssets,总资产(万)
               liquidAssets,流动资产
               fixedAssets,固定资产
               reserved,公积金
               reservedPerShare,每股公积金
               eps,每股收益
               bvps,每股净资
               pb,市净率
               timeToMarket,上市日期
    """
    url = 'http://file.tushare.org/tsdata/all.csv'
    request = Request(url)

    try:

        text = urlopen(request, timeout=10).read()
        text = text.decode('GBK')
        text = text.replace('--', '')
        df = pd.read_csv(StringIO(text), dtype={'code': 'object'})
        #df = df.set_index('code')
    except:
        print("读取《http://file.tushare.org/tsdata/all.csv》错误")
        return

    for index,row in df.iterrows():
        row[0] = gf.code_to_symbol(row[0])
        code = row[0]
        t = tuple(row)
        _updateBasicTableInfo(code,t)






#每年运行一次即可
def is_holiday(startdate='2017-01-01',enddate="2019-12-31"):
    '''
            更新于2019-07-21
            1、接口地址：http://api.goseek.cn/Tools/holiday?date=数字日期，支持https协议。
            2、返回数据：工作日对应结果为 0, 休息日对应结果为 1, 节假日对应的结果为 2
            3、节假日数据说明：本接口包含2017年起的中国法定节假日数据，数据来源国务院发布的公告，每年更新1次，确保数据最新
            4、示例：
            http://api.goseek.cn/Tools/holiday?date=20170528
            https://api.goseek.cn/Tools/holiday?date=20170528
            返回数据：
            {"code":10001,"data":2}
            注：周末无论如何股票不交易，返回1

    '''
    date = datetime.datetime.strptime(startdate, "%Y-%m-%d").date()
    enddate = datetime.datetime.strptime(enddate,"%Y-%m-%d").date()
    while date<=enddate:
        isholiday = 3

        apiUrl = "http://api.goseek.cn/Tools/holiday?date=" + str(date).replace("-","")
        request = Request(apiUrl)
        try:
            response = urlopen(request)
        except:
            raise ValueError
        else:
            response_data = response.read()
        if str(response_data)[-3] == '0':
            if date.weekday()==5 or date.weekday()==6:
                isholiday =1    #周末，无论是否工作日，都返回1
            else:
                isholiday = 0   # 工作日返回0
        else:
            isholiday = 1   # 节假日返回1

        sqlfetch = f"select date from is_holiday where date='{str(date)}'"
        try:
            if not DBHelper().fetchone(sqlfetch):
                sql = f"insert into is_holiday (date,isholiday) VALUES ('{str(date)}','{str(isholiday)}')"
                DBHelper().execute(sql)
                print("是否工作日%s写入数据库成功" % str(date))
            else:
                sql = f"update is_holiday set isholiday='{str(isholiday)}' where date='{str(date)}'"
                DBHelper().execute(sql)
                print("是否工作日%s更新成功" % str(date))
        except:
            raise ValueError
        date = date + datetime.timedelta(days=1)




if __name__ == "__main__":
    #每月运行一次，获取股票最新代码及股票名称
    getAllStock()                            #每月运行一次，定于每月第一个周五上午8:30
    #is_holiday("2020-10-24","2020-12-31")       #每年更新一次即可，下次更新时间：2020年12月28日
    pass
