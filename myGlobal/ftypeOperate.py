#!/usr/bin/env/python
# -*- coding:utf-8 -*-
# Author:zwd
# DateTime:2019/8/9-19:01
# Project:stock
# File:dbOperate

import myGlobal.globalFunction as gf
from myGlobal.myCls.msql import DBHelper

FTYPE_LEN = 16

def set_ftype(value, index, key=1):
    '''
    将value转换二进制并将从右起第index位设置为key
    :param value: 原始值
    :param index: 位数
    :param key: 0或1
    :return: 返回值
    '''
    if index > FTYPE_LEN or index < 1:
        print(f"index参数超过{FTYPE_LEN}，本函数只支持{FTYPE_LEN}位,最小不能低于1")
        return value
    if not 0 <= value <= 65535:
        print("value值必须是0-65535之间")
        return value
    if judgeftype(value,index,key):
        return value
    else:
        if key == 1:
            result = value + (1<<(index-1))            #在第几位
            return result
        elif key == 0:
            result =value - (1<<(index-1))
            return result
        else:
            print("key值只能为0或1")
            return value

def get_ftype(brokercode,stockcode,ts_date):
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

def update_ftype(brokercode,stockcode,ts_date,value):
    stockcode = gf.symbol_to_sqlcode(stockcode)
    sql = f'''
    UPDATE broker_buy_stock_info AS a
    INNER JOIN
    broker_buy_summary AS b ON a.broker_buy_summary_id = b.id 
    SET 
    a.simulate_flag = {value}
    WHERE
    stock_code = '{stockcode}'
    AND broker_code = '{brokercode}'
    AND ts_date = '{ts_date}';
    '''
    try:
        DBHelper().execute(sql)
    except:
        print("sql错误")

def judgeftype(value,index,key=1):
    # if list_bin[len(list_bin)-index] == str(key):
    #     return value
    if not isinstance(value,int):
        try:
            value = int(value)
        except:
            print(f"{value}无法转换成int类型")
            return False
    if index > FTYPE_LEN or index < 1:
        print(f"index参数超过{FTYPE_LEN}，本函数只支持{FTYPE_LEN}位,最小不能低于1")
        return False
    if not 0 <= value <= 65535:
        print("value值必须是0-65535之间")
        return False
    list_bin = list(bin(value)[2:].zfill(FTYPE_LEN))
    if list_bin[len(list_bin) - index] == str(key):
        return True
    else:
        return False
