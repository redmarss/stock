#!/bin/usr/env python
# -*- coding:utf-8 -*-

import myGlobal.globalFunction as gf
import myGlobal.myTime as myTime
import datetime
from myGlobal.myCls.ErrorCls import StockError
from myGlobal.myCls.mylogger import mylogger
from myGlobal.myCls.msql import DBHelper



#Stock类
#输入股票代码，日期作为参数
class Stock(object):
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
        if not isinstance(args[0],str):
            return StockError("code_error",args[1],"not_str_error")
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
            return StockError(args[0], "holiday", "holiday")
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
                    return object.__new__(cls)
            except Exception as e:
                print(e)
                mylogger().error(f"语句{sql}错误，请检查")
                return StockError(args[0], args[1], 'sql_error')

    def __init__(self, stockcode, ts_date):
        self._ts_date = ts_date
        self._stockcode = gf.code_to_symbol(stockcode)

        # 获取股票当日交易信息
        sql_stock = f'select * from stock_trade_history_info where stock_code="{self._stockcode}" and ts_date="{self._ts_date}"'    #stockcode无需转换成数据库格式
        self.__tuplestock = DBHelper().fetchone(sql_stock)          #返回当日交易信息的元组

    # region property
    @property
    def stockcode(self):
        return self._stockcode

    @property
    def ts_date(self):
        return self._ts_date

    @property
    def stockname(self):
        stockcode = gf.code_to_symbol(self._stockcode)
        sql = f'select stockname from stock_basic_table where stockcode="{stockcode}"'
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
    # endregion


    def _getbuyBroker(self):
        '''
        获取该日购买该股票的机构，存入列表
        :return: 返回机构列表
        '''
        broker_list = []
        sql = f"""
        SELECT broker_code FROM
        broker_buy_summary INNER JOIN broker_buy_stock_info 
        WHERE broker_buy_stock_info.broker_buy_summary_id = broker_buy_summary.id
        AND stock_code = '{gf.symbol_to_sqlcode(self._stockcode)}'
        AND ts_date = '{self._ts_date}';
        """
        t = DBHelper().fetchall(sql)
        for i in range(len(t)):
            if t[i] not in broker_list:
                broker_list.append(t[i][0])
        return broker_list


    #根据输入参数（code,ts_date）返回下一个(或多个)交易日的数据存入Stock类
    def _next_some_days(self, startdate=None,days=7):
        '''
            更新于20190613
            返回类型：list,
            len(list)应等于days，list中每个元素应为Stock类型或StockError类
        '''
        if startdate is None:
            startdate = self._ts_date
        else:
            if myTime.isDate(startdate) is False:
                return StockError(self._stockcode,'date_error','date_error').next_some_days(days)

        stocklist=[]
        i = 0
        date = startdate
        #当stocklist函数长度小于days且数据库中有数据
        while len(stocklist) < days:
            if gf.stock_is_tradeday(self._stockcode, date):
                s = Stock(self._stockcode, date)
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

    def _before_some_days(self,startdate=None,days=5):
        if startdate is None:
            startdate = self._ts_date
        else:
            if myTime.isDate(startdate) is False:
                return StockError(self._stockcode,'date_error','date_error').next_some_days(days)
        stocklist = []
        i = 0
        date = startdate


    def MA(self,days=5):
        listStockClass = self._next_some_days(self.ts_date,)




