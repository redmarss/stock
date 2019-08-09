#!/usr/bin/env/python
# -*- coding:utf-8 -*-
# Author:zwd
# DateTime:2019/8/9-19:01
# Project:stock
# File:dbOperate

import myGlobal.globalFunction as gf
from myGlobal.myCls.msql import DBHelper

def _getSimulateFlag(brokercode,stockcode,ts_date):
    '''
    从机构购买股票信息中获取ftype值，以判断是否模拟计算过
    :param brokercode: 机构代码
    :param stockcode: 股票代码
    :param ts_date: 交易日期
    :return: ftype(int值),-1(没有找到该日该机构交易该股票信息)，-2（数据库出错）
    '''
    sql = f"""
    SELECT simulate_flag FROM broker_buy_stock_info inner join broker_buy_summary 
    where broker_buy_stock_info.broker_buy_summary_id=broker_buy_summary.id 
    and stock_code='{gf.symbol_to_sqlcode(stockcode)}' and ts_date='{ts_date}' and broker_code='{brokercode}'
    """
    try:
        t = DBHelper().fetchone(sql)
        if t is not None:               #返回ftype值
            return t[0]
        else:
            return -1                   #找不到机构在当日买卖该股票数据，返回-1
    except:
        return -2                       #数据库语句出错，返回-2

def _setSimulaFlag(brokercode,stockcode,ts_date,ftype):
    flag = _getSimulateFlag(brokercode,stockcode,ts_date)

print(_getSimulateFlag(brokercode='80100185',stockcode='sz000063',ts_date='2017-03-16'))