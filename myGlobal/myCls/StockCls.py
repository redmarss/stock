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
    def __init__(self, code, ts_date):
        #判断日期合规性
        if gf.is_holiday(ts_date) != False:                   #可能返回None,True,False
            print("不是交易日或非法日期")
            return
        #判断股票代码合规性
        if code is None:
            print("股票代码不能为空")
            return
        else:
            code = gf._code_to_symbol(code)

        #判断股票代码是否属于沪深A股
        self._dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss',
                                             db='tushare', charset='utf8')
        try:
            stock_info = self._dbObject.fetchone(table="stock_basic_table", field='stockcode',
                                                 where="stockcode='%s'"%code)
            if stock_info is not None:
                try:
                    self._tuplestock = self._dbObject.fetchone(table='stock_trade_history_info',
                                                               where='stock_code="%s" and ts_date="%s"' %
                                                                     (code, ts_date)
                                                               )
                    self._tsdate = ts_date
                    self._code = code
                except:
                    print("code或ts_date有误或不是交易日")
                    return
            else:                           #非沪深A股，返回
                return
        except:
            mexception.RaiseError(mexception.sqlError)
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

    @property
    def buyprice(self):
        return float(self._buyprice)

    @buyprice.setter
    def buyprice(self,value):
        if not isinstance(value,float):
            raise ValueError("购买价格必须为float类型")
        self._buyprice = value


    @property
    def sellprice(self):
        return float(self._sellprice)

    @sellprice.setter
    def sellprice(self,value):
        if not isinstance(value,float):
            raise ValueError("卖出价格必须为float类型")
        self._sellprice = value



    #根据输入参数（code,ts_date）返回下一个(或多个)交易日的数据存入Stock类
    def next_some_days(self,days=7):
        stocklist=[]
        i = 0
        while len(stocklist) < days:
            date = gf.diffDay(self._tsdate,i)
            if self._code is not None:
                s = Stock(self._code,date)
            else:
                return
            if s.open_price is not None:
                stocklist.append(s)
            i+=1
        return stocklist

    #计算均线价格
    def MA(self,days=5):
        list_MA=[]
        t_MA = gf.getStockPrice(self._code,self._tsdate,0-days)
        for i in range(len(t_MA)):
            list_MA.append(t_MA[i][4])          #收盘价
        s = Series(list_MA)
        return round(s.mean(),2)

s=Stock('600000','2018-01-08')
s.MA(5)
# print(s1[0].ts_date)
