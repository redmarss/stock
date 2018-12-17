#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.mysqlCls as msql
import myGlobal.myCls.StockCls as mstock
import myGlobal.myCls.myException as mexception
import myGlobal.globalFunction as gf

class Broker(object):
    _brokercode = None          #机构代码
    _brokername = None          #机构名称
    _buylist = None             #若构造函数中有日期参数，则返回机构当日购买的股票列表
    _tsdate = None              #交易日期
    _dbObject = None            #数据库连接对象
    # _buyprice = None            #（如果机构有买入股票）买入价
    # _sellprice = None           #(如果机构有买入股票)卖出价
    # _stocklist = None           #用来存放购买股票后几天内的Stock集合

    # 构造函数，如果ts_date不为None,则返回当日该机构买入的股票列表至_buylist
    def __init__(self, broker_code=None, ts_date=None):
        #判断参数合规性
        if broker_code is None:
            print("机构代码不能为空")
            return
        if not isinstance(broker_code,str) or (ts_date is not None and not isinstance(ts_date,str)):
            print("Broker类构造函数参数必须为str")
            return
        if ts_date is not None and gf.is_holiday(ts_date) != False:
            print("不是交易日或非法日期")
            return
        # 创建数据库对象（单例模式）
        self._dbObject = msql.SingletonModel(host='localhost', port='3306',
                                       user='root', passwd='redmarss',
                                       charset='utf8',db='tushare')

        # 先获得机构名称及机构代码
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
                self._buylist = [gf._code_to_symbol(item[0]) for item in t_broker_buy]
            else:       #只有买入股票，没有卖出股票
                pass
        else:           #没有传入日期参数
            self._buylist = None

    #模拟买入，存入数据库，并计算盈利
    def simulate_buy(self, amount=1000):
        if self._tsdate == None:
            print("构造函数日期参数不正确，所以无法模拟买入")
            return
        if self._buylist is not None:                       #买卖股票参数不为空（交易日期必不为空）
            if self._tsdate is None:
                print("错误：_buylist不为空，日期确为空")
                return
            for code in self._buylist:
                s = mstock.Stock(code, self._tsdate)
                t = self._find_buy_sell_stock_price(s)
                if t is not None:
                    buyprice = t[0]
                    sellprice = t[1]
                    self._simulate_tosql(code,buyprice,sellprice,amount)
        else:                                               #当天没有买入股票，则返回
            return

    #将模拟买入信息存入数据库
    #需存入字段为：ts_date,broker_code,stock_code,buy_price,sell_price,amount,gainmoney,gainpercent
    def _simulate_tosql(self, code, buyprice, sellprice, amount):
        #若参数stockbuy或stocksell不为Stock类型，则报错
        if not isinstance(buyprice,float) or not isinstance(sellprice,float):
            mexception.RaiseError(mexception.valueError)
            return

        gainmoney = round(sellprice*1000-buyprice*1000, 2)
        gainpercent = round(gainmoney/(buyprice*amount),4)
        try:
            hasRecord = self._dbObject.fetchall(table="simulate_buy",
                                                where="ts_date='%s' and broker_code='%s' and stock_code='%s'"
                                                      %(self._tsdate,self.broker_code,code))
            if hasRecord is not None:
                self._dbObject.insert(table="simulate_buy",ts_date=self._tsdate,broker_code=self.broker_code,
                                      stock_code=code,buy_price=buyprice,sell_price=sellprice,
                                      amount = amount,gainmoney=gainmoney,gainpercent=gainpercent)
                print("%s机构%s买入%s记录成功"%(self.broker_code,self._tsdate,code))
            else:                           #数据库中已有这条数据
                pass
        except:
            mexception.RaiseError(mexception.sqlError)
            return

    #找出买入卖出价
    def _find_buy_sell_stock_price(self,s):
        if not isinstance(s, mstock.Stock):
            print("_find_buy_sell_stock函数参数需为Stock类型")
            return
        stocklist = s.next_some_days(7)
        print()
        if stocklist is None:
            print("未知错误")
            return
        if gf.ChangeRange(stocklist[0].close_price, stocklist[1].open_price) < 0.08:       #第二天开盘涨幅不超过8%
            buyprice = stocklist[1].open_price  #买入价等于第二天的开盘价
            sellprice = round((stocklist[2].high_price+stocklist[2].low_price)/2.0, 2)
            return buyprice, sellprice
        else:
            return None

    @property
    def broker_code(self):
        return self._brokercode


    @property
    def broker_name(self):
        return self._brokername



