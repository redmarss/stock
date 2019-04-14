#!/bin/usr/env python
#-*- coding: utf-8 -*-

from myGlobal.myCls.mylogger import mylogger
from myGlobal.myCls.StockCls import Stock
import myGlobal.globalFunction as gf
import myGlobal.myTime as mTime
from myGlobal.myCls.msql import DBHelper
import datetime
from abc import ABC,abstractmethod,ABCMeta
from myGlobal.myCls.mylogger import mylogger

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
        PRIMARY KEY (`id`),
        UNIQUE INDEX `id_UNIQUE` (`id` ASC),
        UNIQUE INDEX `broker_UNIQUE` (`ts_date` ASC, `broker_code` ASC, `stock_code` ASC,`ftype` ASC)
        )ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=DEFAULT ;
        ''' % tablename
        DBHelper().execute(sql)

    def simulatebuy(self, tablename,stock_code,ts_date,amount=1000,ftype=1):
        if DBHelper().isTableExists(tablename) is False:        #表不存在，则创建表
            self._createtable(tablename)
        result = self.__CaculateStock(stock_code,ts_date,amount, ftype)
        self.__recordToSql(tablename,result)
        print("%s机构于%s购买%s(%s股)记录成功，策略：（%s）" %(self.broker_code,ts_date,stock_code,amount,ftype))


    #计算相应股票数据，返回元组，后续存入数据库
    def __CaculateStock(self, stock_code,ts_date,amount, ftype):
        switch = {
            1: self.__strategy1(stock_code,ts_date,amount),
            2: self.__strategy2(stock_code,ts_date,amount)
        }
        return switch.get(ftype)


    def __recordToSql(self, tablename,t):
        #策略找不到相关历史数据，t的位置返回None
        if t is None:
            return
        #先去查数据库中是否有这笔记录，没有的话再添加
        ts_date = t[1]
        broker_code = t[2]
        stock_code = t[3]
        ftype= t[13]
        sql = "select * from %s where ts_date='%s' and broker_code='%s' and stock_code='%s' and ftype='%s'" \
             % (tablename,ts_date,broker_code,stock_code,ftype)
        result = DBHelper().fetchall(sql)
        if len(result)==0:
            sql2 = "insert into %s values %s" %(tablename,t)
            try:
                DBHelper().execute(sql2)
            except:
                mylogger().error()



    # region 策略1：上榜后第二天开盘买，第三天开盘卖
    def __strategy1(self,stock_code,ts_date,amount):
        stockA = Stock(stock_code,self.ts_date)     #实例化股票对象，以便后续计算
        t_price = stockA.next_some_days(3)          #从买入当天，取3天数据
        if len(t_price)!=3:
            mylogger().error("无法获取%s于%s前交易数据"%(stock_code,ts_date))
            return
        #计算返回值信息
        ts_date = ts_date
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
        #第一个字段随便设个int值作为id（会自动增长）
        return 0,ts_date,broker_code,stock_code,stock_name,buy_date,sell_date,buy_price,sell_price,get_day,amount,gainmoney,gainpercent,ftype
    # endregion


    def __strategy2(self,stock_code,ts_date,amount):
        pass

