#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.mysqlCls as msql
import myGlobal.myCls.StockCls as mstock
import myGlobal.globalFunction as gf

class Broker(object):
    _brokercode = None          #机构代码
    _brokername = None          #机构名称
    _buylist = None             #若构造函数中有日期参数，则返回机构当日购买的股票列表
    _tsdate = None              #交易日期
    _dbObject = None            #数据库连接对象

    # 构造函数，如果ts_date不为None,则返回当日该机构买入的股票列表至_buylist
    @gf.typeassert(broker_code=str, ts_date=(str,type(None)))       #ts_date类型可为str及None
    def __init__(self, broker_code, ts_date=None):
        #判断是否交易日期
        if ts_date is not None and gf.is_holiday(ts_date) is not False:
            print("不是交易日或非法日期")
            return
        #buylist置空
        self._buylist = []
        # 创建数据库对象（单例模式）
        self._dbObject = msql.SingletonModel(host='localhost', port='3306',
                                       user='root', passwd='redmarss',
                                       charset='utf8',db='tushare')

        # 获得机构名称及机构代码
        broker_info = self._dbObject.fetchone(table='broker_info', field='broker_code,broker_name',
                                        where="broker_code='%s'" % (broker_code))
        if broker_info is not None:             #查询出来的机构不为空
            self._brokercode = broker_info[0]
            self._brokername = broker_info[1]
        else:
            print("查不到机构代码为%s的机构"%broker_code)
            return

        #如果传入参数中包含ts_date，则返回buy_list
        if ts_date is not None:
            self._tsdate = ts_date
            t_broker_buy = self._dbObject.fetchall(table='broker_buy_stock_info as a,broker_buy_summary as b',
                                             field='a.stock_code',
                                             where='a.broker_buy_summary_id=b.id and b.broker_code="%s" and b.ts_date="%s"' % (broker_code, ts_date))
            if len(t_broker_buy) != 0:                       #tbroker长度为0，说明找不到对应的数据
                for stock in t_broker_buy:
                    stock = gf._code_to_symbol(stock[0])
                    if gf.isStockA(stock):
                        self._buylist.append(str(stock))
            else:       #只有买入股票，没有卖出股票
                pass
        else:           #没有传入日期参数
            self._buylist = None

    #模拟买入，存入数据库，并计算盈利
    @gf.typeassert(amount=int)
    def simulate_buy(self, amount=1000):
        if self._tsdate is None:
            print("构造函数日期参数不正确，所以无法模拟买入")
            return
        if len(self._buylist) != 0:                       #买卖股票参数不为空（交易日期必不为空）
            for code in self._buylist:
                s = mstock.Stock(code, self._tsdate)
                if s.code is not None:
                    t = self._find_buy_sell_stock_price(s)
                    if t is not None:
                        buyprice = t[0]
                        sellprice = t[1]
                        self._simulate_tosql(code,buyprice,sellprice,amount)
        else:                                               #当天没有买入股票，则返回
            return

    #将模拟买入信息存入数据库
    #需存入字段为：ts_date,broker_code,stock_code,buy_price,sell_price,amount,gainmoney,gainpercent
    @gf.typeassert(code=str, buyprice=float, sellprice=float, amount=int)
    def _simulate_tosql(self, code, buyprice, sellprice, amount):
        gainmoney = round(sellprice*1000-buyprice*1000, 2)
        gainpercent = round(gainmoney/(buyprice*amount),4)
        hasRecord = self._dbObject.fetchall(table="simulate_buy",
                                            where="ts_date='%s' and broker_code='%s' and stock_code='%s'"
                                                  %(self._tsdate,self.broker_code,code))
        if len(hasRecord) == 0:             #数据库中没有相关记录
            self._dbObject.insert(table="simulate_buy",ts_date=self._tsdate,broker_code=self.broker_code,
                                  stock_code=code,buy_price=buyprice,sell_price=sellprice,
                                  amount = amount,gainmoney=gainmoney,gainpercent=gainpercent)
            print("%s机构%s买入%s记录成功"%(self.broker_code,self._tsdate,code))
        else:                           #数据库中已有这条数据
            print("数据库中已有%s机构于%s购买%s的记录"%(self._brokercode,self._tsdate,code))


    #找出买入卖出价
    @gf.typeassert(s=mstock.Stock, day=int)
    def _find_buy_sell_stock_price(self,s,day=7):
        stocklist = s._next_some_days(day)
        if stocklist is None:
            print("未知错误")
            return
        if len(stocklist)==0 or len(stocklist)<day-4:            #如果获取天数为7天，最终获取结果小于3天，则报错
            print("交易记录不足三天")
            return
        if gf.ChangeRange(stocklist[0].close_price, stocklist[1].open_price) < 0.08:       #第二天开盘涨幅不超过8%
            buyprice = stocklist[1].open_price  #买入价等于第二天的开盘价
            sellprice = stocklist[2].open_price
            return float(buyprice), float(sellprice)
        else:
            return None

    @property
    def broker_code(self):
        return self._brokercode


    @property
    def broker_name(self):
        return self._brokername
