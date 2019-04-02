#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.msql as msql
from urllib.request import Request,urlopen
import datetime
from inspect import signature
from functools import wraps
import json

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

@typeassert((str,type(None)))
def code_to_symbol(code):
    '''
    格式化股票代码，与数据库中股票基本信息表做（stock_basic_table）对比
    :param code: "600000","6000000.sh","sh600000" or None
    :return:(str)sh600000、sz000001 or None
    '''
    if code is None:
        return
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare',
                                   charset='utf8')
    if len(code) == 6:
        _code = 'sh'+code if code[:1] in ["6"] else 'sz'+code   #6打头为上海，其余为深圳

    elif len(code) > 6:
        if code[:1].lower() == 's':
            _code = code[2:8]
            _code = 'sh'+_code if _code[:1] in ["6"] else 'sz'+_code
        elif code[-2].lower() == 's':
            _code = code[:6]
            _code = 'sh' + _code if _code[:1] in ["6"] else 'sz' + _code
        else:
            _code = code
    else:                   #code长度不足6位
        _code = "error"

    tcode = dbObject.fetchone(table="stock_basic_table",field="stockcode",where="stockcode='%s'"%_code)
    if tcode is not None:
        return str(tcode[0])
    else:
        print("所输入代码[%s]非沪深A股"%code)
        return


@typeassert((str,type(None)))
def isStockA(stock):
    code = code_to_symbol(stock)
    if code is None:
        return False
    else:
        return True

@typeassert(str)
def isBroker(code):
    '''
    判断code是否机构代码
    :param code: str类型，机构代码
    :return: 如果从broker_info找到相应代码，则返回True，否则返回False
    '''
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare',
                                   charset='utf8')
    t = dbObject.fetchone(table="broker_info",where="broker_code='%s'"%code)
    if t is not None:
        return True
    else:
        return False

@typeassert(str,float,float)
def isLimit(code, openPrice, nowPrice):
    '''
    判断该股票是否涨停板，名称中含S的股票（ST，S），涨幅为5%，超出涨幅则返回None
    :param code:股票代码（str）
    :param openPrice: 开盘价（基准价）(float)
    :param nowPrice: 收盘价或现价(float)
    :return:涨停返回True，未涨停返回False，超出涨幅则返回None
    '''
    #格式化参数
    code = code_to_symbol(code)
    if code is None:            #所输入代码非沪深A股
        return
    #获取股票名称
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare', charset='utf8')
    namelist = dbObject.fetchone(table='stock_basic_table', field='stockname', where='stockcode="%s"'%code)
    name = str(namelist[0])


    if name.upper().find('S')>0:                #名字中包含S，涨幅为5%
        if nowPrice == round(1.05*openPrice, 2):
            return True
        elif nowPrice > round(1.05*openPrice, 2):
            print("超出每日限制涨幅")
            return
        else:
            return False
    else:
        if nowPrice == round(1.1*openPrice, 2):
            return True
        elif nowPrice > round(1.1*openPrice, 2):
            print("超出每日限制涨幅")
            return
        else:
            return False

@typeassert(float,float)
def RaiseOrFall(open, close):
    '''
    判断股票涨或跌，涨返回True，跌或平返回False
    :param open:开盘价（基准价）（float）
    :param close: 收盘价（现价）(float)
    :return: 涨返回True，跌或平返回False,参数错误返回None
    '''
    if open < close:
        return True
    else:
        return False

@typeassert(float,float)
def ChangeRange(priceLastClose,priceNow):
    '''
        输入两个价格，返回幅度
        priceLastClose:昨日收盘价（今日开盘基准价）
        priceNow:今日收盘价或现价
        返回：涨幅，保留4位小数
    '''
    changerange = (priceNow-priceLastClose)/priceLastClose
    return round(changerange, 4)

@typeassert(str)
def is_holiday(date):
    '''
    #判断是否为交易日(休息日)，工作日返回False or 节假日返回True
    :param date: 日期
    :return: 工作日返回FALSE，节假日返回True，日期输入有误返回None
    '''
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare', charset='utf8')
    flag = dbObject.fetchone(table='is_holiday',field='isholiday',where='date="%s"'%date)
    if flag is not None:
        if flag[0] == '1':
            return True
        else:
            return False
    else:
        print("日期输入错误")
        return None

@typeassert(str, str)
def is_tradeday(code, ts_date):
    '''
    判断股票在数据库中是否有交易数据
    :param code: 股票代码
    :param tsdate: 交易日期
    :return: True or False 参数错误返回None
    '''
    if code is None or ts_date is None:
        return
    dbHelp = msql.DBHelper()
    sql = "select * from stock_trade_history_info where stock_code='%s' and ts_date='%s'" % (code, ts_date)
    if dbHelp.fetchone(sql) is not None:            #查询到交易记录
        return True
    else:
        return False

@typeassert(str)
def lastTddate(strdate):
    '''
    返回上一交易日
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



#将byte数据Post至jar服务中
def postData(textByte,urlPost,flag=None):
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
                if flag is None:
                    #print(response.recordCount)
                    print("龙虎榜数据完成,%s条数据导入成功" % dictResponse['recordCount'])
                elif flag == "stock":
                    pass
                else:
                    pass
        else:
            pass
    except Exception as e:
        print(e)




@typeassert(table=str)
def getAllBroker(table):
    broker_list=[]
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare',
                                   charset='utf8')
    t_broker = dbObject.fetchall(table=table, field="broker_code")
    for t in t_broker:
        if t[0] not in broker_list:
            broker_list.append(t[0])
    return broker_list

def getAllStock(where='1=1'):
    li = []
    # 创建数据库对象（单例模式）
    dbObject = msql.SingletonModel(host='localhost', port='3306',
                                         user='root', passwd='redmarss',
                                         charset='utf8', db='tushare')
    t_stock = dbObject.fetchall(table="stock_basic_table",field="stockcode", where=where,order="stockcode")
    for key in t_stock:
        li.append(key[0])
    return li



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


