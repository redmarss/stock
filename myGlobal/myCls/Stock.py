#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.msql as msql
import myGlobal.globalFunction as gf
import datetime
from pandas import Series

#Stock类
#输入股票代码，日期作为参数
class Stock(object):
    @gf.typeassert(code=str, ts_date=str)
    def __init__(self, code, ts_date):
        if gf.isStockA(code) is not True:
            print("%s不是沪深A股" % code)
            return 
        #股票代码标准化
        code = gf.code_to_symbol(code)
        #判断参数合规性
        if not gf.is_tradeday(code, ts_date):                   #可能返回None,True,False
            print("%s在%s未查询到交易记录" % (code, ts_date))
            return
        #创建数据库对象（单例模式）
        self.dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss',
                                            db='tushare', charset='utf8')
        # 获取股票当日交易信息
        self.tuplestock = self.dbObject.fetchone(table='stock_trade_history_info',
                                                  where='stock_code="%s" and ts_date="%s"' % (code, ts_date))
        self.ts_date = ts_date
        self.code = code

    @property
    def code(self):
        if self.tuplestock is not None:
            return str(self.tuplestock[1])
        else:
            return None

    @property
    def ts_date(self):
        if self.tuplestock is not None:
            return str(self.tuplestock[2])
        else:
            return None

    @property
    def open_price(self):
        if self.tuplestock is not None:
            return float(self.tuplestock[3])
        else:
            return None

    @property
    def close_price(self):
        if self.tuplestock is not None:
            return float(self.tuplestock[4])
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
        if self.tuplestock is not None:
            return float(self.tuplestock[6])
        else:
            return None

    @property
    def volume(self):
        if self.tuplestock is not None:
            return float(self.tuplestock[7])
        else:
            return None


    #根据输入参数（code,ts_date）返回下一个(或多个)交易日的数据存入Stock类
    @gf.typeassert(days=int)
    def next_some_days(self, days=7):
        '''
            参数示例：7，‘7’，‘7s'
            返回类型：list,list,None
            len(list)应等于days，list中每个元素应为Stock类型
        '''
        if self.code is None:
            return
        stocklist=[]
        i = 0
        date = self.ts_date         #str类型
        #当stocklist函数长度小于days且数据库中有数据
        while len(stocklist) < days:
            if gf.is_tradeday(str(self.code), str(date)):
                s = Stock(self.code, date)
                stocklist.append(s)
            date = gf.diffDay(date, 1)
            # 如果日期最终大于”今天”，则中断循环，否则死循环
            if datetime.datetime.strptime(date, "%Y-%m-%d").date() > datetime.datetime.today().date():
                break
        return stocklist

    #计算买入卖出策略，stype为各种策略编号
    #返回ts_date,broker_code,stock_code,buy_date,sell_date,buy_price,sell_price,amount,gainmoney,gainpercent
    @gf.typeassert(broker_code=str, amount=int, stype=int)
    def strategy(self, broker_code, amount, stype):
        if self.ts_date is None:
            return
        #第一种策略:第二天开盘买，第三天开盘卖
        if stype == 1:
            return self.__strategy1(broker_code,amount)


    #实现第一种策略:第二天开盘买，第三天开盘卖
    def __strategy1(self, broker_code, amount):
        dict1 = {}
        price_list = self.next_some_days(3)
        if len(price_list) != 3:
            return
        #第二天开盘涨幅超过8%，不买了
        if gf.ChangeRange(price_list[0].close_price, price_list[1].open_price) > 0.08:
            return
        dict1['ts_date'] = self.ts_date
        dict1['broker_code'] = broker_code
        dict1['stock_code'] = self.code
        dict1['buy_date'] = gf.diffDay(self.ts_date, 1)
        dict1['sell_date'] = gf.diffDay(self.ts_date, 2)
        dict1['buy_price'] = price_list[1].open_price
        dict1['sell_price'] = price_list[2].open_price
        dict1['amount'] = amount
        dict1['gainmoney'] = round((dict1['sell_price'] - dict1['buy_price']) * amount, 2)
        dict1['gainpercent'] = round(dict1['gainmoney']/(dict1['buy_price']*amount), 2)
        dict1['ftype'] = '1'
        return dict1



    #计算均线价格
    @gf.typeassert(days=int)
    def MA(self, days=5):
        '''
            参数示例：5，‘5’，‘5s'
            返回类型：float,float,None
        '''
        list_MA=[]
        t_MA = gf.getStockPrice(self.code, self.ts_date, 0-days)
        for i in range(len(t_MA)):
            list_MA.append(t_MA[i][4])          #收盘价
        s = Series(list_MA)
        return round(s.mean(), 2)


