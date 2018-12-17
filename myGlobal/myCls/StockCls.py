#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.mysqlCls as msql
import myGlobal.globalFunction as gf
import datetime
from pandas import Series
import myGlobal.myCls.myException as mexception

#Stock类
#输入股票代码，日期作为参数
class Stock(object):
    _tuplestock = None         #存入股票代码，股票交易信息的的元组
    _dbObject = None            #数据库对象
    _tsdate = None              #交易日期
    _code = None                #股票代码

    def __init__(self, code=None, ts_date=None):
        #判断参数合规性
        if code is None or ts_date is None:
            print("Stock类的构造函数中存在空值")
            return
        if not isinstance(code,str) or not isinstance(ts_date,str):
            print("Stock类的参数必须为str类型")
            return
        if gf.is_holiday(ts_date) != False:                   #可能返回None,True,False
            print("不是交易日或非法日期")
            return
        #创建数据库对象（单例模式）
        self._dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss',
                                             db='tushare', charset='utf8')
        #股票代码标准化
        code = gf._code_to_symbol(code)

        if gf.isStockA(code) == True:               #如果是沪深A股
            self._tuplestock = self._dbObject.fetchone(table='stock_trade_history_info',
                                                       where='stock_code="%s" and ts_date="%s"' %
                                                             (code, ts_date)
                                                       )            #获取股票当日交易信息
            self._tsdate = ts_date
            self._code = code

        else:                                       #非沪深A股，返回
            print("该股票代码非沪深A股代码")
            return


    @property
    def code(self):
        if self._tuplestock is not None:
            return str(self._tuplestock[1][-6:])
        else:
            return None

    @property
    def ts_date(self):
        if self._tuplestock is not None:
            return str(self._tuplestock[2])
        else:
            return None

    @property
    def open_price(self):
        if self._tuplestock is not None:
            return float(self._tuplestock[3])
        else:
            return None

    @property
    def close_price(self):
        if self._tuplestock is not None:
            return float(self._tuplestock[4])
        else:
            return None

    @property
    def high_price(self):
        if self._tuplestock is not None:
            return float(self._tuplestock[5])
        else:
            return None

    @property
    def low_price(self):
        if self._tuplestock is not None:
            return float(self._tuplestock[6])
        else:
            return None

    @property
    def volume(self):
        if self._tuplestock is not None:
            return float(self._tuplestock[7])
        else:
            return None



    #根据输入参数（code,ts_date）返回下一个(或多个)交易日的数据存入Stock类
    def next_some_days(self,days=7):
        '''
            参数示例：7，‘7’，‘7s'
            返回类型：list,list,None
            len(list)应等于days，list中每个元素应为Stock类型
        '''
        if not isinstance(days, int):
            try:
                days = int(days)
            except:
                print("next_some_days函数days参数错误")
                return
        stocklist=[]
        i = 0
        date = self._tsdate
        #当stocklist函数长度小于days或者 最终日期小于数据库中最后一天（否则会死循环）
        while len(stocklist) < days:
            if date is not None:
                s = Stock(self._code,date)
                stocklist.append(s)
            date = gf.diffDay(date, 1)
        return stocklist

    #计算均线价格
    def MA(self,days=5):
        '''
            参数示例：5，‘5’，‘5s'
            返回类型：float,float,None
        '''
        if not isinstance(days, int):
            try:
                days = int(days)
            except:
                print("MA函数days参数错误")
                return
        list_MA=[]
        t_MA = gf.getStockPrice(self._code,self._tsdate,0-days)
        for i in range(len(t_MA)):
            list_MA.append(t_MA[i][4])          #收盘价
        s = Series(list_MA)
        return round(s.mean(),2)

# s=Stock('600000','2018-01-08')
# print(s.next_some_days())
# input()
# print(s1[0].ts_date)
