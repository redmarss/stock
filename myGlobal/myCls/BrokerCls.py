#!/usr/bin/env/python
# -*- coding:utf-8 -*-
# Author:zwd
# DateTime:2019/8/25-00:01
# Project:stock
# File:BrokerCls
import myGlobal.globalFunction as gf
import myGlobal.myTime as mt
from myGlobal.myCls.mylogger import mylogger
from myGlobal.myCls.ErrorCls import BrokerError
from myGlobal.myCls.msql import DBHelper


class Broker(object):
    def __new__(cls, *args, **kwargs):
        '''
        初始化Broker类并判断参数是否合规
        :param args:args[0]:机构代码，args[0]:交易日期
        :param kwargs:
        :return: 前往init函数
        '''
        if not mt.isDate(args[1]):
            print(f"{args[1]}不是日期格式")
            return BrokerError(args[0], "date_error")
        sql_broker = f"select broker_code from broker_info where broker_code={args[0]}"
        try:
            t = DBHelper().execute(sql_broker)
            if len(t) == 0:
                print(f"{args[0]}不是合法的机构代码")
                return BrokerError("BrokerCodeError", args[1])
            else:
                return super.__new__(cls)
        except:
            mylogger().error(f"数据库语句错误：{sql_broker}")
            return BrokerError(args[0],args[1],"sql_error")

    #构造函数，参数为brokercode,ts_date
    def __init__(self,brokercode,ts_date):
        self._brokercode = brokercode
        self._ts_date = ts_date

    #获取该日期broker_code购买的股票列表
    def _getBuyStock(self):
        stocklist = []
        #查询当天该机构购买的股票列表
        sql_brokerbuy = f'''SELECT stock_code,stock_name,broker_code,ts_date FROM 
                            broker_buy_stock_info info
                            INNER JOIN
                            broker_buy_summary summary 
                            ON info.broker_buy_summary_id = summary.id
                            WHERE
                            summary.broker_code = '{self._brokercode}'
                            AND summary.ts_date = '{self._ts_date}';'''
        t_broker_buy = DBHelper().fetchall(sql_brokerbuy)
        if len(t_broker_buy) > 0:
            for stock in t_broker_buy:
                stock = gf.code_to_symbol(str(stock[0]))
                if stock not in stocklist:
                    stocklist.append(stock)
        return stocklist

    @property
    def brokercode(self):
        return self._brokercode

    @property
    def ts_date(self):
        return self._ts_date










