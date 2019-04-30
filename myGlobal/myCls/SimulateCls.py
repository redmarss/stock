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
        `getscore` VARCHAR(20) NULL,
        PRIMARY KEY (`id`),
        UNIQUE INDEX `id_UNIQUE` (`id` ASC),
        UNIQUE INDEX `broker_UNIQUE` (`ts_date` ASC, `broker_code` ASC, `stock_code` ASC,`ftype` ASC)
        )ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=DEFAULT ;
        ''' % tablename
        DBHelper().execute(sql)

    def simulatebuy(self, tablename,stock_code,ts_date,amount=1000,ftype=1):
        if stock_code =='code_error':               #非沪深A股
            return
        if DBHelper().isTableExists(tablename) is False:        #表不存在，则创建表
            self._createtable(tablename)
        # #判断broker_buy_stock_info中simulate_flag状态，如果与ftype相等，则说明已写入，return
        # sql = "SELECT simulate_flag FROM broker_buy_stock_info as a,broker_buy_summary as b where b.ts_date='%s' and b.broker_code='%s' and a.broker_buy_summary_id=b.id and a.stock_code like '%s%%'"%
        # (ts_date,self.broker_code,stock_code[:6])
        # t = DBHelper().execute(sql)[0]
        # #判断simulate_flag在ftype是否写入过数据库
        # if self.__is_simulate(t,ftype) is False:        #已写入过数据库
        #     return

        result = self.__CaculateStock(stock_code,ts_date,amount, ftype)
        self.__recordToSql(tablename,result)
        self.__update_brokerbuystockinfo(ftype)


    def __is_simulate(self, t, ftype):
        if t & (1<<(ftype-1))>0:            #数字t的第ftype位为1
            return True
        else:
            return False


    # def __get_simulate_flag(self,broker_code,ts_date,stock_code):
    #     sql = "SELECT simulate_flag FROM broker_buy_stock_info as a,broker_buy_summary as b where b.ts_date='%s' and b.broker_code='%s' and a.broker_buy_summary_id=b.id and a.stock_code like '%s%%'"%
    #     (ts_date,self.broker_code,stock_code[:6])

    # #更新simulate_flag状态
    # def __update_brokerbuystockinfo(self,ftype):
    #     #取得broker_buy_stock_info数据库中当前状态




    #计算相应股票数据，返回元组，后续存入数据库
    def __CaculateStock(self, stock_code,ts_date,amount, ftype):
        # switch = {
        #     1: self.__strategyOpenbuyOpensell(stock_code,ts_date,amount,ftype),
        #     2: self.__strategyOpenbuyOpensell(stock_code,ts_date,amount,ftype)
        # }
        # return switch.get(ftype)
        return self.__strategyOpenbuyOpensell(stock_code,ts_date,amount,ftype)

    def __recordToSql(self, tablename,t):
        #策略找不到相关历史数据，t的位置返回None
        if t is None:
            return
        #先去查数据库中是否有这笔记录，没有的话再添加
        ts_date = t[1]
        broker_code = t[2]
        stock_code = t[3]
        ftype= t[13]
        amount=t[10]
        sql = "select * from %s where ts_date='%s' and broker_code='%s' and stock_code='%s' and ftype='%s'" \
             % (tablename,ts_date,broker_code,stock_code,ftype)
        result = DBHelper().fetchall(sql)
        if len(result)==0:
            sql2 = "insert into %s values %s" %(tablename,t)
            try:
                DBHelper().execute(sql2)
                print("%s机构于%s购买%s(%s股)记录成功，策略：（%s）" % (self.broker_code, ts_date, stock_code, amount, ftype))
            except:
                mylogger().error()

    #根据策略类型及其他相关数据计算此次得分
    def __cacuscore(self,ftype,gainmoney,gainpercent):
        return gainpercent



    # region 策略1(2)：上榜后第二天开盘买，第三(四)天开盘卖
    def __strategyOpenbuyOpensell(self,stock_code,ts_date,amount,ftype):
        stockA = Stock(stock_code,self.ts_date)     #实例化股票对象，以便后续计算
        t_price = stockA.next_some_days(int(ftype)+2)          #从买入当天，取3天数据
        if len(t_price)!= int(ftype)+2:
            mylogger().error("无法获取%s于%s买入后%s天交易数据"%(stock_code,ts_date,int(ftype)+2))
            return
        #第二天开盘涨幅大于8%，不买
        if gf.ChangeRange(t_price[0].close_price,t_price[1].open_price) > 0.08:
            return
        #计算返回值信息
        ts_date = ts_date
        broker_code = self.broker_code
        stock_code = stock_code
        stock_name = stockA.name
        buy_date = mTime.diffDay(ts_date,1)
        sell_date = mTime.diffDay(ts_date,int(ftype)+1)
        buy_price = t_price[1].open_price
        sell_price = t_price[int(ftype)+1].open_price
        get_day = ftype             #持有天数
        amount= amount
        gainmoney = round((sell_price-buy_price) * amount, 2)
        gainpercent = round(gainmoney/(buy_price*amount), 4)
        ftype = ftype
        getscore = self.__cacuscore(ftype,gainmoney,gainpercent)
        #第一个字段随便设个int值作为id（会自动增长）
        return 0,ts_date,broker_code,stock_code,stock_name,buy_date,sell_date,buy_price,sell_price,get_day,amount,gainmoney,gainpercent,ftype,getscore
    # endregion




