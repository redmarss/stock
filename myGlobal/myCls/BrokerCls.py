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
        sql_broker = f"select broker_code from broker_info where broker_code='{args[0]}'"   #查询机构代码是否合法语句
        try:
            t = DBHelper().fetchall(sql_broker)
            if len(t) == 0:
                if not mt.isDate(args[1]):
                    print(f"'{args[0]}'不是合法机构代码且'{args[1]}'不是合法日期格式")
                    return BrokerError("broker_error", "date_error", "broker_date_all_error")
                else:
                    print(f"{args[0]}不是合法的机构代码")
                    return BrokerError("broker_error", args[1], "broker_error")
            elif not mt.isDate(args[1]):
                print(f"'{args[1]}'不是有效的日期格式")
                return BrokerError(args[0], "date_error","date_error")
            else:
                return super().__new__(cls)
        except Exception as e:
            print(e)
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


if __name__ == '__main__':
    b = Broker("10000018","2019-08-112")
    print(b)
    print(b.brokercode)
    print(b.ts_date)
    print(b.msg)







