#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.globalFunction as gf
import myGlobal.myCls.msql as msql
import myGlobal.myTime as mTime
from myGlobal.myCls.Stock import Stock
import datetime
import Run.DailyRun as DailyRun

class Broker(object):

    def __init__(self,broker_code):
        #判断机构代码是否在broker_info表中
        if gf.isBroker(broker_code) is True:
            self.broker_code = broker_code
            self.dbObject = msql.SingletonModel(host='localhost', port='3306',
                                       user='root', passwd='redmarss',
                                       charset='utf8',db='tushare')
        else:
            print("机构代码%s不在broker_info表中，请重试" % broker_code)
            self.broker_code = None
            return

    def getBuyStock(self, ts_date):
        li_buy_stock = []
        if self.broker_code is not None:
            if gf.is_holiday(ts_date) is False:
                t_broker_buy = self.dbObject.fetchall(table='broker_buy_stock_info as a,broker_buy_summary as b',
                                                      field='a.stock_code',
                                                      where='a.broker_buy_summary_id=b.id and b.broker_code="%s" and b.ts_date="%s"'
                                                            % (self.broker_code, ts_date))
                if len(t_broker_buy) > 0:
                    for stock in t_broker_buy:
                        stock = gf.code_to_symbol(str(stock[0]))
                        if gf.isStockA(stock) and stock not in li_buy_stock:
                            li_buy_stock.append(stock)
            else:
                pass
        return li_buy_stock


class BrokerSimulate(Broker):
    #构造函数
    def __init__(self, broker_code, startdate, enddate):
        if mTime.isDate(startdate) is True and mTime.isDate(enddate) is True:
            Broker.__init__(self, broker_code)
            self.startdate = mTime.strTodate(startdate)
            self.enddate = mTime.strTodate(enddate)
            self.dbObject = msql.SingletonModel(host="localhost", port="3306", user="root", passwd="redmarss",
                                                db="tushare", charset="utf8")
        else:
            print("输入的日期参数不合法")
            self.startdate = None
            self.enddate = None


    @gf.typeassert(table=str)
    def __createtable(self, table):
        sql = '''
        CREATE TABLE `tushare`.`%s` (
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
        '''%table
        if self.dbObject.isTableExists(table=table) is False:
            self.dbObject.execute(sql)
            print("创建表%s成功" % table)
        else:
            print("%s表已存在" % table)
            return

    @gf.typeassert(tablesimulate=str, amount=int,ftype=int)
    def simulatebuy(self, tablesimulate, amount=1000,ftype=1):
        #若开始日期或结束日期或机构编码为空，说明构造函数输入错误，返回
        if self.startdate is None or self.enddate is None or self.broker_code is None:
            return
        #如果table表不存在，则创建
        if self.dbObject.isTableExists(tablesimulate) is False:
            self.__createtable(tablesimulate)
        #开始循环
        date = self.startdate
        while date <= self.enddate:
            #获取当日所购买股票
            li_stock = self.getBuyStock(str(date))
            if len(li_stock) > 0:                   #有购买股票，则记录
                for stock in li_stock:
                    self.__recordToSql(str(date), stock, amount, tablesimulate,ftype)
            date = date + datetime.timedelta(days=1)

    #按顺序写入ts_date,broker_code,stock_code,buy_date,sell_date,buy_price,sell_price,amount,gainmoney,gainpercent
    @gf.typeassert(ts_date=str, stock_code=str, amount=int, tablesimulate=str,ftype=int)
    def __recordToSql(self, ts_date, stock_code, amount, tablesimulate,ftype):
        stockA = Stock(stock_code, ts_date)
        dict_info = stockA.strategy(self.broker_code, amount, ftype)
        if dict_info is not None:               #若dict_info为空，则说明不符合买入条件
            try:
                self.dbObject.insert(table=tablesimulate,
                                     ts_date=dict_info['ts_date'],broker_code=dict_info['broker_code'],
                                     stock_code=dict_info['stock_code'],buy_date=dict_info['buy_date'],
                                     sell_date=dict_info['sell_date'],buy_price=dict_info['buy_price'],
                                     sell_price=dict_info['sell_price'],amount=dict_info['amount'],
                                     gainmoney=dict_info['gainmoney'],gainpercent=dict_info['gainpercent'],
                                     ftype=dict_info['ftype'])
                print("%s于%s购买%s记录成功" % (self.broker_code, ts_date, stock_code))

            except Exception as e:
                print("数据库中已存在%s于%s购买%s的记录" % (self.broker_code, ts_date, stock_code))



    #根据输入的机构表，记录这些机构模拟买卖信息
    gf.typeassert(table=str,where=str,reason=str)
    def everyday_stock_record(self,table,where,reason):
        li_broker = []
        try:                #判断table是否合法
            t = self.dbObject.fetchall(field="broker_code", table=table, where=where)
            for i in range(len(t)):
                li_broker.append(str(t[i][0]))              #将选出的broker_code以str方式放入li_broker
        except:
            print("数据库参数有误，请重新输入")
            return
        start = datetime.datetime.strptime(self.startdate, "%Y-%m-%d").date()
        end = datetime.datetime.strptime(self.enddate, "%Y-%m-%d").date()
        tsdate = start
        while tsdate <= end:
            if gf.is_holiday(str(tsdate)) is False:
                li_stock = []
                #计算当天股票
                t1 = DailyRun.getStockEveryDay(str(tsdate))
                for i in range(len(t1)):
                    li_stock.append(str(t1[i][0]))
                #存入数据库
                if len(li_stock) > 0:
                    for stock in li_stock:
                        self._everyday_stock_simulate_buy(str(tsdate), stock, reason, 1000)
            tsdate = tsdate + datetime.timedelta(days=1)

    @gf.typeassert(tsdate=str,stock=str,amount=(int,type(None)), money=float)
    def _everyday_stock_simulate_buy(self, tsdate, stock, reason, amount=None, money=10000.0):     #若数量为空，则根据money除以股价计算amount
        stock = gf.code_to_symbol(stock)
        if stock is None:
            return
        st = Stock(stock, tsdate)
        if st.open_price is not None:
            if amount is None:
                amount = int((money//(st.open_price*100))*100)
        gainmoeny = st.gainmoney(amount)
        if gainmoeny is None:               #第二天涨幅超过8%，无法买入
            return
        t = self._dbObject.fetchone(table="everyday_buy",where="ts_date='%s' and stock='%s'"%(tsdate,stock))
        if t is None:
            self._dbObject.insert(table="everyday_buy",ts_date=tsdate,stock=stock,amount=amount,gainmoney=gainmoeny,
                                  reason=reason)






