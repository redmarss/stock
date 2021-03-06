#!/usr/bin/env/python
# -*- coding:utf-8 -*-
# Author:zwd
# DateTime:2019/8/19-23:05
# Project:stock
# File:Strategy

import myGlobal.myTime as mt
import myGlobal.globalFunction as gf
from myGlobal.myCls.mylogger import mylogger
from myGlobal.myCls.Stock import Stock

class Strategy(Stock):
    def __init__(self,stockcode,tsdate,brokercode,ftype,amount):
        self._stockcode = gf.code_to_symbol(stockcode)
        self._ts_date = tsdate
        self._brokercode = brokercode
        self._ftype = ftype
        self._amount = amount


    def strategy(self):
        switch = {
            1: self.__strategyOpenbuyOpensell(),
            2: self.__strategyOpenbuyOpensell()
        }
        return switch.get(self._ftype)

    #策略1:第二天开盘买入，第三天开盘卖出
    def __strategyOpenbuyOpensell(self):
        GET_DAY_NUM=3
        t_price = self._next_some_days(self._ts_date,GET_DAY_NUM)  # 从买入当天，取3天数据
        if len(t_price) != GET_DAY_NUM:
            print(f"无法获取{self._stockcode}于{self._ts_date}买入后{self._ftype+2}天交易数据(停牌一个月以上)")
            return "SUSPENSION_ERROR"
        # 第二天开盘涨幅大于8%，不买
        if gf.ChangeRange(t_price[0].close_price, t_price[1].open_price) > 0.08:
            return "HIGH_OPEN_ERROR"
        # 计算返回值信息
        ts_date = self._ts_date
        broker_code = self._brokercode
        stock_code = self._stockcode
        stock_name = self.stockname
        buy_date = mt.diffDay(ts_date, 1)
        sell_date = mt.diffDay(ts_date, GET_DAY_NUM-1)
        buy_price = t_price[1].open_price
        sell_price = t_price[2].open_price
        get_day = GET_DAY_NUM-2  # 持有天数
        amount = self._amount
        gainmoney = round((sell_price - buy_price) * amount, 2)
        gainpercent = round(gainmoney / (buy_price * amount), 4)
        ftype = self._ftype
        getscore = self._cacuscore(gainmoney, gainpercent)
        # 第一个字段随便设个int值作为id（会自动增长）
        return 0, ts_date, broker_code, stock_code,stock_name,buy_date,sell_date,buy_price,sell_price,get_day,amount,gainmoney,gainpercent,ftype,getscore

    #根据策略类型及其他相关数据计算此次得分
    def _cacuscore(self,gainmoney,gainpercent):
        return gainpercent

if __name__ == '__main__':
    print(Strategy("600733","2018-09-28","80000038",1,1000).strategy())
