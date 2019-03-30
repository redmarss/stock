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
    def _CaculateStock(self, amount=1000, ftype=1):
        switch = {
            1: self._strategy1(amount),
            2: self._strategy2(amount)
        }
        switch.get(ftype)

    def _recordToSql(self, ts_date, amount, ftype):
        li_stock = self.getBuyStock(ts_date)
        if len(li_stock)>0:
            for stock_code in li_stock:
                stockA = Stock(stock_code, ts_date)
                dict_info = stockA.strategy(self.broker_code, amount, ftype)
                if dict_info is not None:               #若dict_info为空，则说明不符合买入条件
                    try:
                        self.dbObject.insert(table=self.tablename,
                                             ts_date=dict_info['ts_date'],broker_code=dict_info['broker_code'],
                                             stock_code=dict_info['stock_code'],buy_date=dict_info['buy_date'],
                                             sell_date=dict_info['sell_date'],buy_price=dict_info['buy_price'],
                                             sell_price=dict_info['sell_price'],amount=dict_info['amount'],
                                             gainmoney=dict_info['gainmoney'],gainpercent=dict_info['gainpercent'],
                                            ftype=dict_info['ftype'])
                        print("%s于%s购买%s记录成功" % (self.broker_code, ts_date, stock_code))

                    except Exception as e:
                        print("数据库中已存在%s于%s购买%s的记录" % (self.broker_code, ts_date, stock_code))

    def _strategy1(self,amount):
        pass

    def _strategy2(self,amount):
        pass

#根据输入的股票代码，开始、结束日期，写入table表
class StockSimulate(Stock, Simulate):
    def __init__(self, stock_code, tablename, startdate, enddate):
        Simulate.__init__(self, tablename, startdate, enddate)
        self.code = stock_code



    # #根据输入的机构表，记录这些机构模拟买卖信息
    # gf.typeassert(table=str,where=str,reason=str)
    # def everyday_stock_record(self,table,where,reason):
    #     li_broker = []
    #     try:                #判断table是否合法
    #         t = self.dbObject.fetchall(field="broker_code", table=table, where=where)
    #         for i in range(len(t)):
    #             li_broker.append(str(t[i][0]))              #将选出的broker_code以str方式放入li_broker
    #     except:
    #         print("数据库参数有误，请重新输入")
    #         return
    #     start = datetime.datetime.strptime(self.startdate, "%Y-%m-%d").date()
    #     end = datetime.datetime.strptime(self.enddate, "%Y-%m-%d").date()
    #     tsdate = start
    #     while tsdate <= end:
    #         if gf.is_holiday(str(tsdate)) is False:
    #             li_stock = []
    #             #计算当天股票
    #             t1 = DailyRun.getStockEveryDay(str(tsdate))
    #             for i in range(len(t1)):
    #                 li_stock.append(str(t1[i][0]))
    #             #存入数据库
    #             if len(li_stock) > 0:
    #                 for stock in li_stock:
    #                     self._everyday_stock_simulate_buy(str(tsdate), stock, reason, 1000)
    #         tsdate = tsdate + datetime.timedelta(days=1)
    #
    # @gf.typeassert(tsdate=str,stock=str,amount=(int,type(None)), money=float)
    # def _everyday_stock_simulate_buy(self, tsdate, stock, reason, amount=None, money=10000.0):     #若数量为空，则根据money除以股价计算amount
    #     stock = gf.code_to_symbol(stock)
    #     if stock is None:
    #         return
    #     st = Stock(stock, tsdate)
    #     if st.open_price is not None:
    #         if amount is None:
    #             amount = int((money//(st.open_price*100))*100)
    #     gainmoeny = st.gainmoney(amount)
    #     if gainmoeny is None:               #第二天涨幅超过8%，无法买入
    #         return
    #     t = self._dbObject.fetchone(table="everyday_buy",where="ts_date='%s' and stock='%s'"%(tsdate,stock))
    #     if t is None:
    #         self._dbObject.insert(table="everyday_buy",ts_date=tsdate,stock=stock,amount=amount,gainmoney=gainmoeny,
    #                               reason=reason)

#
# s = BrokerSimulate("80033529","str1","2019-01-01","2019-01-31")
# s.simulatebuy()