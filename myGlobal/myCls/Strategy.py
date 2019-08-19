#!/usr/bin/env/python
# -*- coding:utf-8 -*-
# Author:zwd
# DateTime:2019/8/19-23:05
# Project:stock
# File:Strategy

import myGlobal.myTime as mt
import myGlobal.globalFunction as gf
from myGlobal.myCls.mylogger import mylogger
from myGlobal.myCls.BrokerCls import Broker
from myGlobal.myCls.Stock import Stock

class Strategy(Broker,Stock):
    def __init__(self,brokercode,stockcode,tsdate,ftype,amount):
        Broker(brokercode,tsdate)
        Stock(stockcode,tsdate)
        self._amount = amount
        try:
            self._ftype = int(ftype)
        except:
            print(f"{ftype}无法转换为int类型")


    def strategy(self):
        switch = {
            1: self.__strategyOpenbuyOpensell(),
            2: self.__strategyOpenbuyOpensell()
        }
        return switch.get(self._ftype)

    #策略1:第二天开盘买入，第三天开盘卖出；策略2：第二天开盘买入，第四天开盘卖出
    def __strategyOpenbuyOpensell(self):
        t_price = self.next_some_days(self._ftype + 2)  # 从买入当天，取ftype+2天数据
        if len(t_price) != int(self._ftype) + 2:
            mylogger().error(f"无法获取{self.brokercode}于{self.ts_date}买入后{self._ftype+2}天交易数据")
            return
        # 第二天开盘涨幅大于8%，不买
        if gf.ChangeRange(t_price[0].close_price, t_price[1].open_price) > 0.08:
            return
        # 计算返回值信息
        ts_date = self.ts_date
        broker_code = self.brokercode
        stock_code = self.code
        stock_name = self.name
        buy_date = mt.diffDay(ts_date, 1)
        sell_date = mt.diffDay(ts_date, int(self._ftype) + 1)
        buy_price = t_price[1].open_price
        sell_price = t_price[self._ftype+ 1].open_price
        get_day = self._ftype  # 持有天数
        amount = self._amount
        gainmoney = round((sell_price - buy_price) * amount, 2)
        gainpercent = round(gainmoney / (buy_price * amount), 4)
        ftype = self._ftype
        getscore = self.__cacuscore(ftype, gainmoney, gainpercent)
        # 第一个字段随便设个int值作为id（会自动增长）
        return 0, ts_date, broker_code, stock_code,stock_name,buy_date,sell_date,buy_price,sell_price,get_day,amount,gainmoney,gainpercent,ftype,getscore