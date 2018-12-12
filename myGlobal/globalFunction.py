#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.mysqlCls as msql
import myGlobal.myCls.myException as mexception
from urllib.request import Request,urlopen
import datetime

#将字符串格式的日期形式转换为date形式，出错则返回None
def strConvertdate(strdate):
    try:
        date = datetime.datetime.strptime(strdate, "%Y-%m-%d").date()
        return date
    except:
        mexception.RaiseError(mexception.dateError)
        return None

#获取所有股票代码
#返回格式为列表[{'stockcode':'600000','stockname':'浦发银行'},{}...{}]
def getAllStockCode():
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare', charset='utf8')
    liststcok = dbObject.fetchall(table='stock_basic_table', field='stockcode,stockname')
    return liststcok

#生成代码标志
#存在多种形式，如"600000","6000000.sh","sh600000"
#需转换成"sh600000"
def _code_to_symbol(code):
    if len(code) != 6:
        if code[:1] in ['5','6','9']:
            return 'sh%s'%code[:6]
        elif code[:1] in ['0','1','2','3','4','7','8']:
            return 'sz%s'%code[:6]
        else:
            return code
    else:
        return 'sh%s' % code if code[:1] in ['5', '6', '9'] else 'sz%s' % code

#判断是否涨停板,若涨停，返回True，否则返回False;含S的股票名称（ST,S）,涨幅为5%,超出涨幅返回空
def isLimit(code, openPrice, nowPrice):
    if isinstance(code,str)==False:
        code = str(code)
    if isinstance(openPrice,float)==False:
        open = float(openPrice)
    if isinstance(nowPrice,float)==False:
        price = float(nowPrice)

    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare', charset='utf8')
    namedict = dbObject.fetchone(table='stock_basic_table', field='stockname', where='stockcode="%s"'%code)
    if namedict is not None:
        name=str(namedict['stockname'])
    else:
        mexception.RaiseError(mexception.codeError)
        return

    if name.upper().find('S')>0:                #名字中包含S，涨幅为5%
        if price == round(1.05*open, 2):
            return True
        elif price>round(1.05*open, 2):
            print("超出每日限制涨幅")
            return
        else:
            return False
    else:
        if price == round(1.1*open, 2):
            return True
        elif price > round(1.1*open, 2):
            print("超出每日限制涨幅")
            return
        else:
            return False

#判断股票涨或跌，涨返回True，跌或平返回False
def RaiseOrFall(open, close):
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
    range = (priceNow-priceLastClose)/(priceLastClose)
    return round(range, 4)

#判断是否为交易日，工作日返回False or 节假日返回True
def is_holiday(date):
    if date is None:
        return None
    if not isinstance(date, str):
        date = str(date)
    strConvertdate(date)
    dbObject = msql.SingletonModel(host='localhost',port='3306',user='root',passwd='redmarss',db='tushare',charset='utf8')
    flag = dbObject.fetchone(table='is_holiday',field='isholiday',where='date="%s"'%date)
    if flag[0] == '1':
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
    date = strConvertdate(strdate)
    if date is not None:
        if day > 0:
            while day > 0:
                date = date+datetime.timedelta(days=1)
                if not is_holiday(date):                #若非休息日，day-1
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

