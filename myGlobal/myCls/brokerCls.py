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
    _stocklist = None
    # 构造函数，如果ts_date不为None,则返回当日该机构买入的股票列表至_buylist
    def __init__(self, broker_code, ts_date=None):
        dbObject = msql.SingletonModel(host='1localhost', port='3306',
                                       user='root', passwd='redmarss',
                                       charset='utf8',db='tushare',mycursor='list')

        # 先获得机构名称及机构代码
        broker_info = dbObject.fetchone(table='broker_info', field='broker_code,broker_name',
                                        where="broker_code='%s'" % (broker_code))
        if broker_info is not None:             #查询出来的机构不为空
            self._brokercode = broker_info[0]['broker_code']
            self._brokername = broker_code[0]['broker_name']
        else:
            mexception.RaiseError(mexception.brokerError)
            return

        #如果传入参数中包含ts_date，则返回buy_list
        if ts_date is not None:
            self._tsdate = ts_date
            t_broker_buy = dbObject.fetchall(table='broker_buy_stock_info as a,broker_buy_summary as b',
                                             field='a.stock_code',
                                             where='a.broker_buy_summary_id=b.id and b.broker_code="%s" and b.ts_date="%s"' % (broker_code, ts_date))
            if len(t_broker_buy) != 0:                       #tbroker长度为0，说明找不到对应的数据
                self._buylist = [gf._code_to_symbol(item[0]) for item in t_broker_buy]
            else:
                print("该机构当天没有买卖股票")
        else:
            self._buylist = None

    #将模拟买入信息存入数据库
    #需存入字段为：ts_date,broker_code,stock_code,buy_price,sell_price,amount,gainmoney,gainpercent
    def simulate_tosql(self, stockbuy, stocksell):
        #若参数stockbuy或stocksell不为Stock类型，则报错
        if not isinstance(stockbuy,mstock.Stock) or not isinstance(stocksell,mstock.Stock):
            mexception.RaiseError(mexception.typeError)
            return

    #模拟买入，存入数据库，并计算盈利
    def simulate_buy(self,amount):
        if self._tsdate == None:
            print("构造函数未输入日期参数，所以找不到买卖股票信息")
            return
        dbObject = msql.SingletonModel(host="localhost", port="3306",
                                       user="root", passwd="redmarss",
                                       db="tushare", charset="utf8")
        if self._buylist is not None:                       #买卖股票参数不为空（交易日期必不为空）
            for code in self._buylist:
                s = mstock.Stock(code, self._tsdate)
                self._stocklist = s.next_some_days(7)




    @property
    def broker_code(self):
        return self._brokercode


    @property
    def broker_name(self):
        return self._brokername



if __name__ == '__main__':
    #b=Broker('80467525')
    A=mstock.Stock('600000','2018-01-08')
    b=Broker('80467525','2018-06-22')
    b.simulate_tosql("test",A)
