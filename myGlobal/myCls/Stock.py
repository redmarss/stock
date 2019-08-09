#!/bin/usr/env python
# -*- coding:utf-8 -*-

import myGlobal.globalFunction as gf
import myGlobal.myTime as myTime
import datetime
import pandas as pd
from myGlobal.myCls.ErrorCls import StockError
from decimal import Decimal
from myGlobal.myCls.mylogger import mylogger
from myGlobal.myCls.msql import DBHelper
#定义日志类及路径
#mylogger=mylogger()


#Stock类
#输入股票代码，日期作为参数
class Stock(object):
    @gf.typeassert(args=str)
    def __new__(cls, *args,**kwargs):
        '''
        更新日期：20190613
        判断code是否合规；
        判断日期是否合规；
        合规后运行init函数，否则报错并退出
        :param args[0]:股票代码
        :param args[1]: 交易日期
        :return: 跳转至__init__函数
        '''
        #1.判断股票代码是否合规
        code = gf.code_to_symbol(args[0])
        #股票代码不合法
        if code.startswith("code_error"):       #包含code_error(None),code_error(NotA),code_error(Else)
            print("股票代码不合法")
            #股票代码不合法，日期也不合法
            if myTime.isDate(args[1]) is False:
                return StockError('code_error', 'date_error', 'code_date_all_error')
            #股票代码不合法，但日期合法
            else:
                return StockError('code_error', args[1], 'code_error')
        #股票代码合法，日期不合法
        elif myTime.isDate(args[1]) is False:            #日期不合法
            print("日期格式不合法")
            return StockError(args[0], 'date_error', 'date_error')
            #日期合法，但是休息日
        elif gf.is_holiday(args[1]) is True:
            print(f"{args[1]}是休息日")
            return StockError(args[0], args[1], "holiday")
        else:
            #不判断日期、代码是否合法，直接读数据库
            sql = f"select * from stock_trade_history_info where stock_code='{code}' and ts_date='{args[1]}'"
            try:
                t = DBHelper().fetchall(sql)
                #停牌
                if len(t) == 0:
                    print(f"没有找到{code}股票在{args[1]}交易记录")
                    return StockError(args[0], args[1], 'suspension')       #停牌
                else:
                    #去往初始化函数
                    return super().__new__(cls)
            except:
                mylogger().error(f"语句{sql}错误，请检查")
                return StockError(args[0], args[1], 'sql_error')

    def __init__(self, code, ts_date):
        self._ts_date = ts_date
        self._code = gf.code_to_symbol(code)

        # 获取股票当日交易信息
        sql_stock = f'select * from stock_trade_history_info where stock_code="{self._code}" and ts_date="{self._ts_date}"'
        self.__tuplestock = DBHelper().fetchone(sql_stock)

    # region property
    @property
    def code(self):
        return self._code

    @property
    def ts_date(self):
        return self._ts_date

    @property
    def name(self):
        sql = f'select stockname from stock_basic_table where stockcode="{self._code}"'
        t = DBHelper().fetchone(sql)[0]
        return t

    @property
    def open_price(self):
        if self.__tuplestock is not None:
            return float(self.__tuplestock[3])
        else:
            return None

    @property
    def close_price(self):
        if self.__tuplestock is not None:
            return float(self.__tuplestock[4])
        else:
            return None

    @property
    def high_price(self):
        if self.__tuplestock is not None:
            return float(self.__tuplestock[5])
        else:
            return None

    @property
    def low_price(self):
        if self.__tuplestock is not None:
            return float(self.__tuplestock[6])
        else:
            return None

    @property
    def volume(self):
        if self.__tuplestock is not None:
            return float(self.__tuplestock[7])
        else:
            return None
    @property
    def getbuyBroker(self):
        broker_list = []
        sql = f"""
        SELECT broker_code FROM
        broker_buy_summary INNER JOIN broker_buy_stock_info 
        WHERE broker_buy_stock_info.broker_buy_summary_id = broker_buy_summary.id
        AND stock_code LIKE '{self.code[2:]}%'
        AND ts_date = '{self.ts_date}';
        """
        t = DBHelper().fetchall(sql)
        for i in range(len(t)):
            if t[i] not in broker_list:
                broker_list.append(t[i][0])
        return broker_list
    # endregion

    #根据输入参数（code,ts_date）返回下一个(或多个)交易日的数据存入Stock类
    def next_some_days(self, startdate=None,days=7):
        '''
            更新于20190613
            返回类型：list,
            len(list)应等于days，list中每个元素应为Stock类型或StockError类
        '''
        if startdate is None:
            startdate = self._ts_date
        else:
            if myTime.isDate(startdate) is False:
                return StockError(self._code,'date_error','date_error').next_some_days(days)

        stocklist=[]
        i = 0
        date = startdate
        #当stocklist函数长度小于days且数据库中有数据
        while len(stocklist) < days:
            if gf.stock_is_tradeday(self._code, date):
                s = Stock(self._code, date)
                stocklist.append(s)
            date = myTime.diffDay(date, 1)          #已自动跳过双休日
            if date is None:
                #date为None，说明diffDay参数date格式非法，在此函数中“应该”不会出现
                pass
            tempdate = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            # 如果停牌一个月以上，则中断循环
            if tempdate > datetime.datetime.strptime(startdate, "%Y-%m-%d").date()+datetime.timedelta(days=days+30):
                break
        return stocklist

    #计算买入卖出策略，stype为各种策略编号
    #返回ts_date,broker_code,stock_code,buy_date,sell_date,buy_price,sell_price,amount,gainmoney,gainpercent
    def strategy(self, broker_code, amount, ftype):
        # if self._ts_date is None:
        #     return
        #第一种策略:第二天开盘买，第三天开盘卖
        if ftype == 1:
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
        dict1['ts_date'] = self._ts_date
        dict1['broker_code'] = broker_code
        dict1['stock_code'] = self._code
        dict1['buy_date'] = myTime.diffDay(self._ts_date, 1)
        dict1['sell_date'] = myTime.diffDay(self._ts_date, 2)
        dict1['buy_price'] = price_list[1].open_price
        dict1['sell_price'] = price_list[2].open_price
        dict1['amount'] = amount
        dict1['gainmoney'] = round((dict1['sell_price'] - dict1['buy_price']) * amount, 2)
        dict1['gainpercent'] = round(dict1['gainmoney']/(dict1['buy_price']*amount), 2)
        dict1['ftype'] = '1'
        return dict1

    # @gf.typeassert(days=int)
    # def getStockInfo(self, days=7):
    #     '''
    #     获取某股票N个交易日内的所有数据,返回元组
    #     :param code: 股票代码
    #     :param startdate: 开始日期
    #     :param days: 天数
    #     :return: 股票交易信息（元组）
    #     '''
    #     code = self._code
    #     if code is None:
    #         return
    #     field_list = ["a.id", "a.stock_code", "a.ts_date", "a.open_price", "a.close_price", "a.high_price",
    #                   "a.low_price", "a.volume", "b.k", "b.d", "b.j"]
    #     field = ""
    #     for i in field_list:
    #         field += "%s," % i
    #     field = field.rstrip(",")
    #     t = self._dbObject.fetchall(table='stock_trade_history_info as a,qualification as b',
    #                                 field=field,
    #                                 where="a.stock_code=b.stock_code and a.ts_date=b.ts_date and "
    #                                       "a.stock_code='%s' and a.ts_date%s='%s' order by a.ts_date desc"
    #                                       % (code, ('>' if days > 0 else '<'), self._ts_date),
    #                                 limit=str(abs(days)))
    #
    #     return pd.DataFrame(list(t),columns=field_list)

    #计算均线价格
    # @gf.typeassert(days=int)
    # def MA(self, days=5):
    #     '''
    #         参数示例：5
    #         返回类型：float,float,None
    #     '''
    #     if days not in [5,10,15,20,30,60,120,250,360]:
    #         print("MA参数不符合定义")
    #         return
    #     list_MA=[]
    #     df_MA = self.getStockInfo(0-days)
    #     if df_MA.shape[0]>=days:
    #         return round(df_MA['a.close_price'].mean(), 2)
    #     else:                                       #数据长度不足，返回0.0
    #         return 0.0
    #
    #
    # def getMA(self,*args):
    #     for i in args:
    #         ma = self.MA(i)
    #         field = "MA"+str(i)
    #         self._writeQualifi(field,ma)
    #
    #
    # @gf.typeassert(N=int)
    # def KDJ(self, N=9):
    #     if N < 0:
    #         print("N值不能为负数")
    #         return
    #     t_stock = None
    #     if self._code is not None and self._ts_date is not None:
    #         df_stock = self.getStockInfo(0-N)
    #         #寻找N日内收盘价
    #         if df_stock.shape[0] < N:
    #             k = d = 50
    #             j = 3 * k - 2 * d
    #             self._writeQualifi(k=k,d=d,j=j)
    #         else:
    #             #n日RSV=（Cn－Ln）/（Hn－Ln）×100
    #             Cn = Decimal.from_float(self.close_price)                     #当日收盘价
    #             Ln = df_stock["a.low_price"].min()                            #N日最低价
    #             Hn = df_stock["a.high_price"].max()                           #N日最高价
    #             Rsv = (Cn-Ln)/(Hn-Ln)*100
    #             #获取前一日K值与D值
    #             k_last = df_stock.loc[1, "b.k"]           #前一日K值
    #             d_last = df_stock.loc[1, "b.d"]           #前一日D值
    #             #当日K值=2/3×前一日K值+1/3×当日RSV
    #             k = round(Decimal.from_float(2/3)*k_last+Decimal.from_float(1/3)*Rsv,2)
    #             d = round(Decimal.from_float(2/3)*d_last+Decimal.from_float(1/3)*k,2)
    #             j = 3*k-2*d
    #
    #             self._writeQualifi(k=k, d=d, j=j)
    #
    #
    # def _writeQualifi(self,*args,**kwargs):
    #     if len(args) !=0:
    #         kwargs[args[0]]=args[1]
    #     for key,value in kwargs.items():
    #         #先判断qualification表中是否有k列，如果没有则添加
    #         try:
    #             #如果原来就有这列，则pass
    #             t = self._dbObject.fetchall(table="qualification",field=key)
    #         except:
    #             #没有这一列，则添加
    #             sql = '''
    #             ALTER TABLE `tushare`.`qualification`
    #             ADD COLUMN `%s` DECIMAL(15,2) NULL;
    #             '''%key
    #             self._dbObject.execute(sql)
    #         #开始写入
    #         stock_code = self._code
    #         ts_date = self._ts_date
    #         t = self._dbObject.fetchall(table="qualification",
    #                                     where="stock_code='%s' and ts_date='%s'" % (stock_code,ts_date))
    #
    #         if len(t) == 0:
    #             sql_insert = "insert into qualification set stock_code='%s',ts_date='%s',%s='%s'"% (stock_code,ts_date,key,value)
    #             self._dbObject.execute(sql_insert)
    #             print("%s(%s)记录成功" % (stock_code, ts_date))
    #         else:
    #             sql_update = "update qualification set %s='%s' where stock_code='%s' and ts_date='%s'" % (key,value,stock_code,ts_date)
    #             self._dbObject.execute(sql_update)
    #             print("%s(%s)更新成功" % (stock_code, ts_date))

        # #取出参数中的技术指标
        # k = kwargs['k']
        # d = kwargs['d']
        # j = kwargs['j']
        #
        # stock_code = self._code
        # ts_date = self._ts_date
        #
        # t = self._dbObject.fetchall(table="qualification",
        #                             where="stock_code='%s' and ts_date='%s'"%(stock_code,ts_date))
        # if len(t) == 0:
        #     self._dbObject.insert(table="qualification",stock_code=stock_code,ts_date=ts_date,
        #                           k=k, d=d, j=j)
        #     print("%s(%s)记录成功"%(stock_code,ts_date))
        # else:
        #     self._dbObject.update(table="qualification",where="stock_code='%s' and ts_date='%s'"%(stock_code,ts_date),
        #                           k=k,d=d,j=j)
        #     print("%s(%s)更新成功" % (stock_code, ts_date))







