#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.mysqlCls as msql
import myGlobal.globalFunction as gf
import datetime
from pandas import Series

#Stock类
#输入股票代码，日期作为参数
class Stock(object):
    _tuplestock = None         #存入股票代码，股票交易信息的的元组
    _dbObject = None            #数据库对象
    _tsdate = None              #交易日期
    _code = None                #股票代码

    @gf.typeassert(code=str, ts_date=str)
    def __init__(self, code, ts_date):
        #股票代码标准化
        code = gf._code_to_symbol(code)
        #判断参数合规性
        if not gf.is_tradeday(code,ts_date):                   #可能返回None,True,False
            print("%s在%s未查询到交易记录" % (code, ts_date))
            return None
        #创建数据库对象（单例模式）
        self._dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss',
                                             db='tushare', charset='utf8')
        self._tuplestock = self._dbObject.fetchone(table='stock_trade_history_info',
                                                   where='stock_code="%s" and ts_date="%s"' %
                                                         (code, ts_date)
                                                   )            #获取股票当日交易信息
        self._tsdate = ts_date
        self._code = code



    @property
    def code(self):
        return self._code

    @property
    def ts_date(self):
        return self._ts_date

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

    @gf.typeassert(amount=int)
    def gainmoney(self, amount=1000):
        if self._tsdate is None:
            return
        day = 3
        stocklist = self._next_some_days(day)
        if stocklist is None:
            return
        elif len(stocklist) == day:
            if gf.ChangeRange(stocklist[0].close_price, stocklist[1].open_price) < 0.08:
                gainmoney = (stocklist[2].open_price - stocklist[1].open_price)*amount
                return round(gainmoney, 2)


    #根据输入参数（code,ts_date）返回下一个(或多个)交易日的数据存入Stock类
    @gf.typeassert(days=int)
    def _next_some_days(self, days=7):
        '''
            参数示例：7，‘7’，‘7s'
            返回类型：list,list,None
            len(list)应等于days，list中每个元素应为Stock类型
        '''
        stocklist=[]
        i = 0
        date = self._tsdate         #str类型
        #当stocklist函数长度小于days且数据库中有数据
        while len(stocklist) < days:
            if gf.is_tradeday(str(self._code),str(date)) :
                s = Stock(self._code, date)
                stocklist.append(s)
            date = gf.diffDay(date, 1)
            # 如果日期最终大于”今天”，则中断循环，否则死循环
            if datetime.datetime.strptime(date, "%Y-%m-%d").date() > datetime.datetime.today().date():
                break
        return stocklist

    #计算均线价格
    @gf.typeassert(days=int)
    def MA(self, days=5):
        '''
            参数示例：5，‘5’，‘5s'
            返回类型：float,float,None
        '''
        list_MA=[]
        t_MA = gf.getStockPrice(self._code, self._tsdate, 0-days)
        for i in range(len(t_MA)):
            list_MA.append(t_MA[i][4])          #收盘价
        s = Series(list_MA)
        return round(s.mean(),2)


