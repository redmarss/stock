#!/bin/usr/env python
#-*- coding: utf-8 -*-

import myGlobal.globalFunction as gf
import myGlobal.ftypeOperate as fto
import myGlobal.myTime as mt
from myGlobal.myCls.Stock import Stock
from myGlobal.myCls.msql import DBHelper
from myGlobal.myCls.mylogger import mylogger
from myGlobal.myCls.BrokerCls import Broker
from myGlobal.myCls.ErrorCls import BrokerSimulateError
from myGlobal.myCls.ErrorCls import BrokerError
from myGlobal.myCls.StrategyCls import Strategy

#根据输入的机构代码，开始、结束日期，写入tablename表
class BrokerSimulate(Broker):
    def __new__(cls, *args, **kwargs):
        '''
        更新日期：20190613
        运行父函数Broker的__new__函数，判断参数args[0],args[1]是否合规，如果不合规，则会返回BrokerError类，再判断
        如果合规，则跳转至__init__函数
        :param args[0]:机构代码
        :param args[1]: 交易日期
        :param args[2]: 模拟策略类型
        :param args[3]: 模拟买入数量
        :param args[4]: 模拟表，默认为:simulate_buy
        :return: 跳转至__init__函数
        '''
        b = super().__new__(cls,*args,**kwargs)
        if isinstance(b,BrokerError):
            if b.msg == "broker_error":
                return BrokerSimulateError("broker_error",args[1],"broker_error")
            elif b.msg == "broker_date_all_error":
                return BrokerSimulateError("broker_error","date_error","broker_date_all_error")
            elif b.msg == "date_error":
                return BrokerSimulateError(args[0],"date_error","date_error")
            elif b.msg == "holiday":
                return BrokerSimulateError(args[0],"holiday","holiday")
            else:
                return BrokerSimulateError(args[0], args[1], "error")
        elif not isinstance(args[2],int):
            return BrokerSimulateError(args[0],args[1],"ftype_error")
        elif not isinstance(args[3],int):
            return BrokerSimulateError(args[0],args[1],"amount_error")
        elif not isinstance(args[4],str):
            return BrokerSimulateError(args[0],args[1],"table_error")
        else:
            return object.__new__(cls)          #跳转至自身的__init__函数


    def __init__(self, brokercode, ts_date, ftype,amount,tablename):#tablename=simulate_buy
        self._brokercode = brokercode
        self._ts_date = ts_date
        self._tablename = tablename
        self._ftype= ftype
        self._amount = amount
        self._buystocklist = super()._getBuyStock()                 #list格式


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
        #计算该机构在ts_date购买股票数，并模拟买入
        if len(self._buystocklist) == 0:
            return False
        for stockcode in self._buystocklist:
            #1.查看simulateflag是否已模拟，如果模拟了，则什么都不做
            if not self.__is_simulate(stockcode,self._ftype):
                #2.模拟买入，并返回一个元组
                strategy = Strategy(stockcode,self._ts_date,self._brokercode,self._ftype,self._amount)
                t = strategy.strategy()
                #3.将元组存入数据库
                result = self.__recordToSql(t)          #如果存入数据库成功，则result为True，否则为False
                if result:
                # 4.更新flag值,并存入数据库
                    self.__update_ftype(stockcode)
                    print(f"模拟{self.brokercode}于{self.ts_date}购买{stockcode}成功，模拟方式：{self._ftype}，购买数量：{self._amount}")
                else:
                    pass
            else:
                pass


    def __is_simulate(self,stockcode,ftype):
        simulate_flag = fto.get_ftype(self._brokercode, stockcode, self._ts_date)
        if fto.judgeftype(simulate_flag, ftype):
            return True
        else:
            return False



    #更新simulate_flag状态
    def __update_ftype(self,stockcode):
        simulate_flag = fto.get_ftype(self._brokercode, stockcode, self._ts_date)
        new_flag = fto.set_ftype(simulate_flag,self._ftype,1)
        result = fto.update_ftype(self._brokercode,stockcode,self._ts_date,new_flag)
        return result

    def __recordToSql(self,t):
        sql_insert = f"insert into {self._tablename} values {t}"
        try:
            result = DBHelper().execute(sql_insert)
            return result
        except:
            mylogger().error()
            return False




if __name__ == '__main__':
    bs = BrokerSimulate("80065939","2017-09-12",1,1000,"simulate_buy")
    bs.simulateBuy()
