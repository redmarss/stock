#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zwd
# DateTime:2020/6/29-8:57
# Project:stock
# File:day_tranding_1


import myGlobal.globalFunction as gf
from myGlobal.myCls.msql import DBHelper
import myGlobal.myTime as mt
from myGlobal.myCls.Stock import Stock


#
def CacuStock(code,strdate):
    s = Stock(code,strdate)     #获取上榜当天龙虎榜信息
    s_next_trade_day =




#获取strdate前一交易日所有龙虎榜股票，返回list
def GetLastLhb(strdate):
    #获取形参的上一个交易日
    lastTradeDay = gf.lastTddate(strdate)
    #选出龙虎榜中该日期的所有上榜股票（不重复）
    select_stock_list = f'''
    SELECT distinct
    stock_code
    FROM
    broker_buy_summary AS a
        INNER JOIN
    broker_buy_stock_info AS b ON a.id = b.broker_buy_summary_id
    WHERE
    ts_date = '{lastTradeDay}'
    '''
    t = DBHelper().fetchall(select_stock_list)
    #将元组中数据存入List并返回
    code_list = []
    for code in t:
        code = code[0]
        code = gf.code_to_symbol(code)
        if code not in code_list:
            code_list.append(code)
    #以list形式返回
    return code_list







if __name__ == '__main__':
    strdate = '2020-01-06'
    code = 'sz000009'

    CacuStock(code,strdate)