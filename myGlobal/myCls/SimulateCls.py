#!/bin/usr/env python
#-*- coding: utf-8 -*-

from myGlobal.myCls.mylogger import mylogger
from myGlobal.myCls.StockCls import Stock
import myGlobal.globalFunction as gf
import myGlobal.myTime as mTime
from myGlobal.myCls.msql import DBHelper
import datetime
from abc import ABC,abstractmethod,ABCMeta

# region Simulate抽象类
class Simulate(metaclass=ABCMeta):                  #抽象类
    def __init__(self, tablename):
        self.tablename = tablename

    @abstractmethod
    def _createtable(self, sql):
        return

    @abstractmethod
    def simulatebuy(self, broker_code, ts_date, stock_code, amount=1000, ftype=1):
        return
# endregion

#根据输入的机构代码，开始、结束日期，写入tablename表
class BrokerSimulate(Simulate):
    def __init__(self, tablename, broker_code,ts_date):
        Simulate.__init__(self, tablename)
        self.broker_code = broker_code
        self.ts_date = ts_date

    def _createtable(self, tablename):
        sql = '''
        CREATE TABLE `tushare`.`%s` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `ts_date` VARCHAR(45) NOT NULL,
        `broker_code` VARCHAR(45) NOT NULL,
        `stock_code` VARCHAR(45) NOT NULL,
        `stock_name` VARCHAR(45) NOT NULL,
        `buy_date` VARCHAR(45) NULL,
        `sell_date` VARCHAR(45) NULL,
        `buy_price` VARCHAR(45) NULL,
        `sell_price` VARCHAR(45) NULL,
        `get_day` VARCHAR(45) NULL,
        `amount` VARCHAR(45) NULL,
        `gainmoney` VARCHAR(45) NULL,
        `gainpercent` VARCHAR(45) NULL,
        `ftype` VARCHAR(5) NULL,
        `cflag` VARCHAR(5) NULL,
        PRIMARY KEY (`id`),
        UNIQUE INDEX `id_UNIQUE` (`id` ASC),
        UNIQUE INDEX `broker_UNIQUE` (`ts_date` ASC, `broker_code` ASC, `stock_code` ASC,`ftype` ASC)
        )ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=DEFAULT ;
        ''' % tablename
        DBHelper().execute(sql)

    def simulatebuy(self, stock_code,amount=1000,ftype=1):
        result = self._CaculateStock(stock_code,amount, ftype)
        self.__recordToSql(result)


    #计算相应股票数据，返回元组，后续存入数据库
    def _CaculateStock(self, stock_code,amount=1000, ftype=1):
        switch = {
            1: self._strategy1(stock_code,amount),
            2: self._strategy2(stock_code,amount)
        }
        return switch.get(ftype)


    def _recordToSql(self, ts_date, amount, ftype):
        pass

    #策略1：上榜后第二天开盘买，第三天开盘卖
    def _strategy1(self,stock_code,amount):
        stockA = Stock(stock_code,self.ts_date)     #实例化股票对象，以便后续计算
        t_price = stockA.next_some_days(3)          #从买入当天，取3天数据
        #计算返回值信息
        ts_date = self.ts_date
        broker_code = self.broker_code
        stock_code = stock_code
        stock_name = stockA.name
        buy_date = mTime.diffDay(ts_date,1)
        sell_date = mTime.diffDay(ts_date,2)
        buy_price = t_price[1].open_price
        sell_price = t_price[2].open_price
        get_day = 1             #持有一天
        amount= amount
        gainmoney = round((sell_price-buy_price) * amount, 2)
        gainpercent = round(gainmoney/(buy_price*amount), 4)
        ftype = 1
        return ts_date,broker_code,stock_code,stock_name,buy_date,sell_date,buy_price,sell_price,get_day,amount,gainmoney,gainpercent,ftype


    def _strategy2(self,amount):
        pass

