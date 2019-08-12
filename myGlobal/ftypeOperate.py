#!/usr/bin/env/python
# -*- coding:utf-8 -*-
# Author:zwd
# DateTime:2019/8/9-19:01
# Project:stock
# File:dbOperate

import myGlobal.globalFunction as gf
from myGlobal.myCls.msql import DBHelper

TYPE_LEN = 16

def list_to_bin(list1):
    if len(set(list1))==2:                          #如果list1中有两个元素，则必须是0和1
        if '1' not in list1 or '0' not in list1:
            return
    if len(set(list1))>=3:                          #如果list1中有三个不同的元素，则报错
        return
    result = 0
    for i in range(len(list1)):
        result = result + list1[len(list1)-i-1]*(2**len(list1)-1-i)
    return result


def set_bit(value, index,key=1):
    '''
    将value转换二进制并将从右起第index位设置为key
    :param value: 原始值
    :param index: 位数
    :param key: 0或1
    :return: 返回值
    '''
    global TYPE_LENLEN
    if index>TYPE_LEN or index < 1:
        print(f"index参数超过{TYPE_LEN}，本函数只支持{TYPE_LEN}位,最小不能低于1")
        return value
    if not 0<=value<=65535:
        print("value值必须是0-65535之间")
        return value
    #判断value的index位是否等于key，如果是，则直接返回value，如果不是，则加上1<<(index-1)
    list_bin = list(bin(value)[2:].zfill(16))
    if list_bin[len(list_bin)-index] == str(key):
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

print(set_bit(1111111111111111117,3,0))