#!/bin/usr/env python
#-*- coding: utf-8 -*-

import myGlobal.globalFunction as gf
import myGlobal.myTime as mTime
from myGlobal.myCls.Stock import Stock
from myGlobal.myCls.msql import DBHelper
from myGlobal.myCls.mylogger import mylogger
from myGlobal.myCls.BrokerCls import Broker


#根据输入的机构代码，开始、结束日期，写入tablename表
class BrokerSimulate(Broker):
    def __init__(self,broker_code,ts_date, tablename='simulate_buy',ftype=1):
        Broker(broker_code,ts_date)
        self._tablename = tablename
        self._ftype= ftype
        self._buystocklist = self.getBuyStock()

    # region _createtable     创建tablename表
    def _createtable(self,tablename):
        sql_create = f"""
        CREATE TABLE `tushare`.`{tablename}` (
        `id` INT NOT NULL AUTO_INCREMENT,
        `ts_date` VARCHAR(45) NOT NULL,
        `broker_code` VARCHAR(45) NOT NULL,
        `stock_code` VARCHAR(45) NOT NULL,
        `buy_date` VARCHAR(45) NULL,
        `sell_date` VARCHAR(45) NULL,
        `buy_price` VARCHAR(45) NULL,
        `sell_price` VARCHAR(45) NULL,
        `amount` VARCHAR(45) NULL,
        `gainmoney` VARCHAR(45) NULL,
        `gainpercent` VARCHAR(45) NULL,
        `ftype` VARCHAR(5) NULL,
        PRIMARY KEY (`id`),
        UNIQUE INDEX `id_UNIQUE` (`id` ASC),
        UNIQUE INDEX `broker_UNIQUE` (`ts_date` ASC, `broker_code` ASC, `stock_code` ASC)
        )ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
        """
        try:
            DBHelper().execute(sql_create)
            print(f"创建{tablename}表成功")
        except:
            mylogger.error(f"创建{tablename}表出错")
    # endregion

    def simulateBuy(self,ftype=1,amount=1000):
        if len(self._buystocklist) > 0:
            for stockcode in self._buystocklist:
                #1.查看simulateflag是否已模拟，如果模拟了，则什么都不做
                #2.模拟买入，并返回一个元组
                t = self._stockbuy(stockcode,ftype, amount)
                #3.将元组存入数据库
                #4.更新flag值

                print(f"模拟{self.brokercode}于{self.ts_date}购买{stockcode}成功，模拟方式：{ftype}，购买数量：{amount}")

    def _stockbuy(self, ftype,stock_code,amount):
        if stock_code.startswith('code_error'):               #非沪深A股
            return
        if DBHelper().isTableExists(self._tablename) is False:        #表不存在，则创建表
            self._createtable(self._tablename)
        # 取出数据库broker_buy_stock_info中simulate_flag状态，然后进行判断
        simulate_flag = self.__get_simulate_flag(stock_code)
        #判断simulate_flag在ftype是否写入过数据库
        if self.__is_simulate(simulate_flag,self.ftype) is True:        #已写入过数据库
            return
        else:

            result = self.__CaculateStock(stock_code,amount, self.ftype)
            self.__recordToSql(result)
            #把broker_buy_stock_info表中simulate_flag状态的第ftype位（从右往左数）置为1 ，表示已计算
            self.__update_brokerbuystockinfo(self.ftype)


    def __is_simulate(self, t, ftype):
        if t & (1<<(ftype-1))>0:            #数字t的第ftype位为1
            return True
        else:
            return False


    def __get_simulate_flag(self,stock_code):
        sql = "SELECT simulate_flag FROM broker_buy_stock_info as a,broker_buy_summary as b where b.ts_date='%s' and b.broker_code='%s' and a.broker_buy_summary_id=b.id and a.stock_code like '%s'" % (
        self._ts_date, self._broker_code, '%%%s%%' % stock_code[2:9])
        t = DBHelper().fetchone(sql)[0]
        return t

    #更新simulate_flag状态
    def __update_brokerbuystockinfo(self,ftype):
        #取得broker_buy_stock_info数据库中当前状态
        simulate_flag = self.__get_simulate_flag()




    #计算相应股票数据，返回元组，后续存入数据库
    def __CaculateStock(self, stock_code,amount, ftype):
        # switch = {
        #     1: self.__strategyOpenbuyOpensell(stock_code,ts_date,amount,ftype),
        #     2: self.__strategyOpenbuyOpensell(stock_code,ts_date,amount,ftype)
        # }
        # return switch.get(ftype)
        return self.__strategyOpenbuyOpensell(stock_code,self._ts_date,amount,ftype)

    def __recordToSql(self,t):
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
            sql2 = "insert into %s values %s" %(self._tablename,t)
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




