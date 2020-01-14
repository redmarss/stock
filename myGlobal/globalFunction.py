#!/bin/usr/env python
# -*- coding:utf-8 -*-
from myGlobal.myCls.msql import DBHelper
from urllib.request import Request,urlopen,HTTPError
import datetime
from inspect import signature
from functools import wraps
import json
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import sys

#装饰函数，限定所有函数的数据类型
def typeassert(*type_args, **type_kwargs):
    def decorate(func):
        sig = signature(func)
        bound_types = sig.bind_partial(*type_args, **type_kwargs).arguments

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs)
            for name, value in bound_values.arguments.items():
                if name in bound_types:
                    if not isinstance(value, bound_types[name]):
                        raise TypeError('{}函数参数{}必须是{},不能为{}'.format(func.__name__, name, bound_types[name],value))
            return func(*args, **kwargs)
        return wrapper
    return decorate

def code_to_symbol(code):
    '''
    标准化股票代码并输出（20190807修改）
    :param code: 股票代码，可接受如【sh600000,600000sh,600000.sh，600000】
    :return: sh600000    若输入错误，返回以code_error开头的字符串
    '''
    if code is None:
        return "code_error(None)"
    if code.startswith(('1','2','4','5','7','8','9')):
        return "code_error(NotA)"                 #去除以2,9开头的代码（B股）
    code = str.lower(code)
    if len(code) == 8 and code.startswith(('sh', 'sz')):              #形似“sh600000,sz000001”，则原样返回
        return 'sh%s'%code[2:] if code[2] in ['6'] else 'sz%s'%code[2:]
    elif len(code) == 9 and code[-3]!=".":
        return "code_error(Else)"
    elif len(code)<=9 and code.endswith(('sh','sz')):              #形似"600000.sh,000001.sz,600000sh,000001sz"，则返回sh600000
        return 'sh'+code[:6] if code[0] in ['6'] else 'sz'+code[:6]
    elif len(code) == 6:
        if code[:].isdigit():
            return 'sh%s'%code if code[:1] in ['6'] else 'sz%s'%code
        else:               #code只有6位且不是全数字，报错
            return "code_error(Else)"
    else:                                               #其余情况则返回None
        return "code_error(Else)"

def symbol_to_sqlcode(code):
    code = code_to_symbol(code)
    if code.startswith('code_error'):
        return code
    else:
        return code[2:]+'.'+code[:2].upper()

def isStockA(code):
    '''
    查询股票是否存于stock_basic_table表中（修改于20190808）
    :param code: 需查询的代码
    :return: True or False
    '''
    symbol = code_to_symbol(code)       #代码标准化
    sql = f"select * from stock_basic_table where stockcode = '{symbol}' and ts_flag=0"             #未退市的A股
    t = DBHelper().fetchall(sql)
    if len(t) > 0:          #查到该股票代码存于stock_basic_table表中
        return True
    else:
        return False

def isBroker(code):
    '''
    判断code是否机构代码(修改于20190808)
    :param code: str类型，机构代码
    :return: 如果从broker_info找到相应代码，则返回True，否则返回False
    '''
    sql = f"select * from broker_info where broker_code ='{code}'"
    t = DBHelper().fetchall(sql)
    if len(t) > 0:
        return True
    else:
        return False

def RaiseOrFall(open, close):
    '''
    判断股票涨或跌，涨返回True，跌或平返回False（修改于20190409）
    :param open:开盘价（基准价）（float）
    :param close: 收盘价（现价）(float)
    :return: 涨返回True，跌或平返回False
    '''
    if open < close:
        return True
    else:
        return False

def ChangeRange(priceLastClose,priceNow):
    '''
        输入两个价格，返回幅度（修改于20190409）
        priceLastClose:昨日收盘价（今日开盘基准价）
        priceNow:今日收盘价或现价
        返回：涨幅，保留4位小数
    '''
    changerange = (priceNow-priceLastClose)/priceLastClose
    return round(changerange, 4)


def is_holiday(date):
    '''
    #判断是否为交易日(休息日)，工作日返回False or 节假日返回True(修改于20190412)
    :param date: 日期(str格式)
    :return: 工作日返回FALSE，节假日返回True，日期输入有误返回None
    '''
    sql = f"select isholiday from is_holiday where date='{date}'"
    flag = DBHelper().fetchone(sql)
    if flag is not None:
        if flag[0] == '1':
            return True
        else:
            return False
    else:
        print("日期输入错误")

def stock_is_tradeday(code, ts_date):
    '''
    判断股票在数据库中是否有交易数据(修改于20190412)
    :param code: 股票代码
    :param tsdate: 交易日期
    :return: True or False 参数错误返回None
    '''
    symbol = code_to_symbol(code)
    sql = f"select * from stock_trade_history_info where stock_code='{symbol}' and ts_date='{ts_date}'"
    t = DBHelper().fetchone(sql)
    if t is not None:            #查询到交易记录
        return True
    else:
        return False

def lastTddate(strdate):
    '''
    返回A股上一交易日（修改于20190412）
    :param strdate: （str）
    :return:不包含当前日期的上一交易日（str）
    '''
    try:
        date = datetime.datetime.strptime(strdate, "%Y-%m-%d").date()
        date = date - datetime.timedelta(days=1)                #先减一天，再判断是否休假
        while is_holiday(str(date)):
            date = date-datetime.timedelta(days=1)
        return str(date)
    except:
        print("日期输入有误")
        return

def postData(textByte,urlPost,flag=None):
    '''
    将byte数据Post至jar服务中
    :param textByte:要推送的byte数据
    :param urlPost: post服务地址
    :param flag: 推送标志，目前有'stock'
    :return: 如果出错，返回出错代码,int值
    '''
    if isinstance(textByte,str):
        textByte=bytes(textByte,encoding='utf8')
    elif isinstance(textByte,bytes):
        pass
    else:
        print('输入文件格式错误')
        return None
    try:
        req=Request(urlPost)
        req.add_header('Content-Type','application/json;charset=utf-8')
        req.add_header('Content-Length',len(textByte))
        response=urlopen(req,textByte).read()
        if len(response) > 0:               #长度大于0，说明能取到正确的字段属性
            dictResponse = json.loads(response)

            if dictResponse['status'] == 200:
                if flag == 'lhb':
                    #print(response.recordCount)
                    print("龙虎榜数据完成,%s条数据导入成功" % dictResponse['recordCount'])
                elif flag == "stock":
                    pass
                else:
                    pass
        else:
            pass
    except HTTPError as e:
        return e.code

def getBroker(table='broker_info',field='broker_code',where='1=1'):
    '''
    从数据表（默认为broker_info）中获取机构代码（修改于20190412）
    :param table:表名，默认为broker_info
    :param field:获取的字段，默认为broker_code
    :param where:筛选条件，默认为全选
    :return:机构列表
    '''
    broker_list=[]
    sql = f' select {field} from {table} where {where}'
    try:
        t_broker = DBHelper().fetchall(sql)
        for t in t_broker:
            if t[0] not in broker_list:
                broker_list.append(t[0])
        return broker_list
    except:
        print('%s出错'%getBroker.__name__)

def getStockFromTable(table='stock_basic_table',field='stockcode',where='1=1'):
    '''
    从数据表stock_basic_table中获取所有股票代码（修改于20190412）
    :param where: 检索条件
    :param table: 检索的表名（默认为stock_basic_table）
    :return: 股票列表
    '''
    li = []
    sql = f'select {field} from {table} where {where} order by stockcode'
    try:
        t_stock = DBHelper().fetchall(sql)
        for key in t_stock:
            if key[0] not in li:
                li.append(key[0])
        return li
    except:
        print('%s出错' % getStockFromTable.__name__)

@typeassert(openPrice=float,nowPrice=float)
def isLimit(code, openPrice, nowPrice , flag=1):
    '''
    判断该股票是否涨停板，名称中含S的股票（ST，S），涨幅为5%，超出涨幅则返回None
    :param code:股票代码（str）
    :param openPrice: 开盘价（基准价）(float)
    :param nowPrice: 收盘价或现价(float)
    :param flag=1为判断是否涨停，flag=-1为判断是否跌停
    :return:涨停返回True，未涨停返回False，超出涨幅则返回None
    '''
    #先判断flag参数是否合规，只能为1或-1
    if flag !=1 or flag!=-1:
        print("flag参数错误，1为判断是否涨停，-1为判断是否跌停")
        return
    #格式化code
    symbol = code_to_symbol(code)
    if symbol is None:            #所输入代码非沪深A股
        return
    #获取股票名称
    sql = "select stockname from stock_basic_table where stockcode = '%s'" % (symbol)
    name = DBHelper().fetchone(sql)[0]

    if name.upper().find('S')>0:                #名字中包含S，涨幅为5%
        if nowPrice == round((1+0.05*flag)*openPrice, 2):
            return True
        elif nowPrice > round((1+0.05*flag)*openPrice, 2):
            print("超出每日限制涨幅")
            return
        else:
            return False
    else:
        if nowPrice == round((1+0.1*flag)*openPrice, 2):
            return True
        elif nowPrice > round((1+0.1*flag)*openPrice, 2):
            print("超出每日限制涨幅")
            return
        else:
            return False







# def find_biggest_day():
#     '''
#     寻找数据库中最后一天（最大的一天）
#     return:日期类型
#     '''
#     dbObject = msql.SingletonModel(host='localhost', port='3306',
#                                    user='root', passwd='redmarss',
#                                    db='tushare', charset='utf8')
#     t_date = dbObject.fetchone(table="broker_buy_summary order by ts_date desc", field="ts_date")
#     return t_date[0]
# def isLimit(code, openPrice, nowPrice):
#     '''
#     判断该股票是否涨停板，名称中含S的股票（ST，S），涨幅为5%，超出涨幅则返回None
#     :param code:股票代码（str）
#     :param openPrice: 开盘价（基准价）(float)
#     :param nowPrice: 收盘价或现价(float)
#     :return:涨停返回True，未涨停返回False，超出涨幅则返回None
#     '''
#     #格式化参数
#     code = code_to_symbol(code)
#     if code is None:            #所输入代码非沪深A股
#         return
#     #获取股票名称
#     dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare', charset='utf8')
#     namelist = dbObject.fetchone(table='stock_basic_table', field='stockname', where='stockcode="%s"'%code)
#     name = str(namelist[0])
#
#
#     if name.upper().find('S')>0:                #名字中包含S，涨幅为5%
#         if nowPrice == round(1.05*openPrice, 2):
#             return True
#         elif nowPrice > round(1.05*openPrice, 2):
#             print("超出每日限制涨幅")
#             return
#         else:
#             return False
#     else:
#         if nowPrice == round(1.1*openPrice, 2):
#             return True
#         elif nowPrice > round(1.1*openPrice, 2):
#             print("超出每日限制涨幅")
#             return
#         else:
#             return False

