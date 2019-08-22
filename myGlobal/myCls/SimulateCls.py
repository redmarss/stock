#!/bin/usr/env python
#-*- coding: utf-8 -*-

import myGlobal.globalFunction as gf
import myGlobal.ftypeOperate as fto
import myGlobal.myTime as mTime
from myGlobal.myCls.Stock import Stock
from myGlobal.myCls.msql import DBHelper
from myGlobal.myCls.mylogger import mylogger
from myGlobal.myCls.BrokerCls import Broker
from myGlobal.myCls.ErrorCls import BrokerSimulateError


#根据输入的机构代码，开始、结束日期，写入tablename表
class BrokerSimulate(Broker):
    def __new__(cls, *args, **kwargs):
        '''
        更新日期：20190613
        判断code是否合规；
        判断日期是否合规；
        合规后运行init函数，否则报错并退出
        :param args[0]:机构代码
        :param args[1]: 交易日期
        :param args[2]: 模拟策略类型
        :param args[3]: 模拟买入数量
        :param args[4]: 模拟表，默认为:simulate_buy
        :return: 跳转至__init__函数
        '''
        #判断args[0]:brokercode是否合法

        #判断args[1]:ts_date是否合法
        if not mTime.isDate(args[1]):
            print(f"{args[1]}非日期格式")
            return BrokerSimulateError(args[0],'date_error')
        else:
            return super().__new__(cls)


    def __init__(self, brokercode, ts_date, ftype=1,amount=1000,tablename='simulate_buy'):
        self._brokercode = brokercode
        self._ts_date = ts_date
        self._tablename = tablename
        self._ftype= ftype
        self._amount = amount
        self._buystocklist = self._getBuyStock()
        print(self._brokercode)
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

    def simulateBuy(self):
        if len(self._buystocklist) > 0:
            for stockcode in self._buystocklist:
                #1.查看simulateflag是否已模拟，如果模拟了，则什么都不做
                if not self.__is_simulate(stockcode,self._ftype):
                    #2.模拟买入，并返回一个元组
                    t = self._stockbuy(stockcode,self.amount)
                    #3.将元组存入数据库
                    if t is not None:
                        pass
                    #4.更新flag值,并存入数据库
                else:
                    pass

                print(f"模拟{self.brokercode}于{self.ts_date}购买{stockcode}成功，模拟方式：{self._ftype}，购买数量：{self._amount}")

    def _stockbuy(self, stock_code):
        if stock_code.startswith('code_error'):               #非沪深A股
            return
        if DBHelper().isTableExists(self._tablename) is False:        #表不存在，则创建表
            self._createtable(self._tablename)
        result = self.__CaculateStock(stock_code, self._ftype,self._amount)
        self.__recordToSql(result)
        #把broker_buy_stock_info表中simulate_flag状态的第ftype位（从右往左数）置为1 ，表示已计算
        self.__update_brokerbuystockinfo(self.ftype)


    def __is_simulate(self,stockcode,ftype,key=1):
        simulate_flag = self.__get_simulate_flag(stockcode)
        if fto.judgeftype(simulate_flag,ftype,key):
            return True
        else:
            return False


    def __get_simulate_flag(self,stockcode):
        sql = f"""
            SELECT simulate_flag FROM
            broker_buy_stock_info AS a
            INNER JOIN
            broker_buy_summary AS b ON a.broker_buy_summary_id = b.id
            WHERE
            broker_code = '{self.brokercode}'
            AND ts_date = '{self.ts_date}'
            AND stock_code = '{gf.symbol_to_sqlcode(stockcode)}';
        """
        t = DBHelper().fetchone(sql)[0]
        return t

    #更新simulate_flag状态
    def __update_brokerbuystockinfo(self,ftype):
        #取得broker_buy_stock_info数据库中当前状态
        simulate_flag = self.__get_simulate_flag()




    # #计算相应股票数据，返回元组，后续存入数据库
    # def __CaculateStock(self, stock_code):
    #     # switch = {
    #     #     1: self.__strategyOpenbuyOpensell(stock_code,ts_date,amount,ftype),
    #     #     2: self.__strategyOpenbuyOpensell(stock_code,ts_date,amount,ftype)
    #     # }
    #     # return switch.get(self._ftype)
    #     return self.__strategy1(stock_code,self._ts_date,self._ftype,self._amount)

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
             % (self._tablename,ts_date,broker_code,stock_code,ftype)
        result = DBHelper().fetchall(sql)
        if len(result)==0:
            sql2 = "insert into %s values %s" %(self._tablename,t)
            try:
                DBHelper().execute(sql2)
                print("%s机构于%s购买%s(%s股)记录成功，策略：（%s）" % (self.broker_code, ts_date, stock_code, amount, ftype))
            except:
                mylogger().error()

    #根据策略类型及其他相关数据计算此次得分
    def _cacuscore(self,ftype,gainmoney,gainpercent):
        return gainpercent



    # region 策略1(2)：上榜后第二天开盘买，第三(四)天开盘卖
    def __strategy1(self,stock_code):
        stockA = Stock(stock_code,self.ts_date)     #实例化股票对象，以便后续计算
        t_price = stockA.next_some_days(int(self._ftype)+2)          #从买入当天，取3天数据
        if len(t_price)!= int(self._ftype)+2:
            mylogger().error("无法获取%s于%s买入后%s天交易数据"%(stock_code,self._ts_date,int(self._ftype)+2))
            return
        #第二天开盘涨幅大于8%，不买
        if gf.ChangeRange(t_price[0].close_price,t_price[1].open_price) > 0.08:
            return
        #计算返回值信息
        ts_date = self._ts_date
        broker_code = self.broker_code
        stock_code = stock_code
        stock_name = stockA.name
        buy_date = mTime.diffDay(ts_date,1)
        sell_date = mTime.diffDay(ts_date,int(self._ftype)+1)
        buy_price = t_price[1].open_price
        sell_price = t_price[int(self._ftype)+1].open_price
        get_day = self._ftype             #持有天数
        amount= self._amount
        gainmoney = round((sell_price-buy_price) * amount, 2)
        gainpercent = round(gainmoney/(buy_price*amount), 4)
        ftype = self._ftype
        getscore = self.__cacuscore(ftype,gainmoney,gainpercent)
        #第一个字段随便设个int值作为id（会自动增长）
        return 0,ts_date,broker_code,stock_code,stock_name,buy_date,sell_date,buy_price,sell_price,get_day,amount,gainmoney,gainpercent,ftype,getscore
    # endregion




if __name__ == '__main__':
    BrokerSimulate("80000000","2019-03-151")
