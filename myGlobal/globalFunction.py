#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.mysqlCls as msql
import myGlobal.myCls.myException as mexception
from urllib.request import Request,urlopen
import datetime


def _code_to_symbol(code):
    '''
    格式化股票代码，与数据库中股票基本信息表做（stock_basic_table）对比
    :param code: "600000","6000000.sh","sh600000" or None
    :return:(str)sh600000、sz000001 or None
    '''
    if not isinstance(code,str):
        code = str(code)
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare',
                                   charset='utf8')
    if code is None:
        _code = "error"
    elif len(code) == 6:
        _code = 'sh'+code if code[:1] in ["6"] else 'sz'+code

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
        print("所输入代码非沪深A股")
        return



#判断是否涨停板,若涨停，返回True，否则返回False;含S的股票名称（ST,S）,涨幅为5%,超出涨幅返回空
def isLimit(code, openPrice, nowPrice):
    '''
    判断该股票是否涨停板，名称中含S的股票（ST，S），涨幅为5%，超出涨幅则返回None
    :param code:股票代码（str）
    :param openPrice: 开盘价（基准价）(float)
    :param nowPrice: 收盘价或现价(float)
    :return:涨停返回True，未涨停返回False，超出涨幅则返回None
    '''
    #格式化参数
    if not isinstance(code, str):
        try:
            code = str(code)
        except:
            print("isLimit函数的code参数无法转换为str")
            return
    if not isinstance(openPrice, float):
        try:
            openPrice = float(openPrice)
        except:
            print("isLimit函数的openPrice参数无法转换为float")
            return
    if not isinstance(nowPrice, float):
       try:
            nowPrice = float(nowPrice)
       except:
           print("isLimit函数的nowPrice参数无法转换为float")
           return
    code = _code_to_symbol(code)
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




def RaiseOrFall(open, close):
    '''
    判断股票涨或跌，涨返回True，跌或平返回False
    :param open:开盘价（基准价）（float）
    :param close: 收盘价（现价）(float)
    :return: 涨返回True，跌或平返回False,参数错误返回None
    '''
    #判断参数合规性
    if not isinstance(open, float):
        try:
            open = float(open)
        except:
            print("RaiseOrFall函数open参数无法转换为float")
            return
    if not isinstance(close, float):
        try:
            close = float(close)
        except:
            print("RaiseOrFall函数close参数无法转换为float")
            return
    if open < close:
        return True
    else:
        return False

#输入两个价格，返回幅度
def ChangeRange(priceLastClose,priceNow):
    '''
        priceLastClose:昨日收盘价（今日开盘基准价）
        priceNow:今日开盘价或现价
        返回：涨幅，保留4位小数
    '''
    if priceLastClose and priceNow is not None:
        range = (priceNow-priceLastClose)/(priceLastClose)
        return round(range, 4)
    else:
        return

#判断是否为交易日，工作日返回False or 节假日返回True
def is_holiday(date):
    if date is None:
        return None
    if not isinstance(date, str):
        date = str(date)
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare', charset='utf8')
    flag = dbObject.fetchone(table='is_holiday',field='isholiday',where='date="%s"'%date)
    if flag is not None:
        if flag[0] == '1':
            return True
        else:
            return False
    else:
        return None


def is_tradeday(code,tsdate):
    '''
    判断股票是否停牌
    :param code: 股票代码
    :param tsdate: 交易日期
    :return: True or False
    '''
    code = _code_to_symbol(code)
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare', charset='utf8')
    istradeday = dbObject.fetchone(table='stock_trade_history_info',where="stock_code='%s' and ts_date='%s'"%(code,tsdate))
    if istradeday is not None:
        return True
    else:
        return False

#返回上一交易日（字符串格式）
def lastTddate(strdate):
    try:
        date = datetime.datetime.strptime(strdate, "%Y-%m-%d").date()
        while is_holiday(str(date))==True:
            date = date-datetime.timedelta(days=1)
        return str(date)
    except:
        print("日期输入有误")

#输入一个日期及天数，返回该日期加上/减去该数量的交易日的结果
def diffDay(strdate,day=0):
    if is_holiday(strdate) == False:
        date = datetime.datetime.strptime(strdate, "%Y-%m-%d").date()
        if day > 0:
            while day > 0:
                date = date+datetime.timedelta(days=1)
                if not is_holiday(date):                #若非休息日，不计入运算
                    day = day-1
        else:
            while day < 0:
                date = date+datetime.timedelta(days=-1)
                if not is_holiday(date):
                    day = day+1
        return str(date)
    else:
        return None

#将byte数据Post至jar服务中
def postData(textByte,urlPost,code=None):
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
        response=urlopen(req,textByte)
        if response.status==200:
            if code is None:
                print("龙虎榜数据完成")
            else:
                print("%s完成"%code)
    except Exception as e:
        if e.code==500:
            print("%s或已退市"%code)
        else:
            print(e)

#获取某股票N个交易日内的所有数据,返回元组
def getStockPrice(code, startdate=None, days=7):
    code = _code_to_symbol(code)
    if startdate==None:
        mexception.RaiseError(mexception.dateError)
        return

    dbObject = msql.SingletonModel(host='localhost', port='3306',
                                   user='root', passwd='redmarss',
                                   db='tushare', charset='utf8')
    if days > 0:            #days大于0，则往后取数字
        try:
            t = dbObject.fetchall(table='stock_trade_history_info',
                                  where="stock_code='%s' and ts_date>='%s'" % (code, startdate),
                                  limit=str(days))
            return t
        except:
            mexception.RaiseError(mexception.sqlError)
            return None
    else:                   #days小于0，往前取
        try:
            t = dbObject.fetchall(table='stock_trade_history_info',
                                  where="stock_code='%s' and ts_date<='%s'" % (code, startdate),
                                  order='ts_date desc',
                                  limit=str(abs(days)))
            return t
        except:
            mexception.RaiseError(mexception.sqlError)
            return None

#获取code是否是沪深A股股票
def isStockA(code):
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare',
                                   charset='utf8')
    isStockA = dbObject.fetchone(table="stock_basic_table", where="stockcode='%s'"%code)
    if isStockA is not None:
        return True
    else:
        return False

#寻找数据库中最后一天（最大的一天）
def find_biggest_day():
    '''
    return:日期类型
    '''
    dbObject = msql.SingletonModel(host='localhost', port='3306',
                                   user='root', passwd='redmarss',
                                   db='tushare', charset='utf8')
    t_date = dbObject.fetchone(table="broker_buy_summary order by ts_date desc", field="ts_date")
    return t_date[0]


