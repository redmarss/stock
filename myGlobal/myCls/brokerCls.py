#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.mysqlCls as msql

class Broker(object):
    _brokercode = None
    _brokername = None
    _buylist = None

    #构造函数，如果ts_date不为None,则返回当日该机构买入的股票列表至_buylist
    def __init__(self, broker_code, ts_date = None):
        dbObject = msql.SingletonModel(host='localhost', port='3306',
                                       user='root', passwd='redmarss',
                                       charset='utf8',db='tushare', mycursor='list')
        if ts_date == None:
            tbroker = dbObject.fetchone(table='broker_info', field='broker_code,broker_name', where="broker_code='%s'" % (broker_code))
        else:
            tbroker = dbObject.fetchall(table='broker_buy_stock_info as a,broker_buy_summary as b', field='a.stock_code',
                                        where='a.broker_buy_summary_id=b.id and b.broker_code="%s" and b.ts_date="%s"' % (broker_code, ts_date))
            self._buylist = [item['stock_code'][:6] for item in tbroker]
        if tbroker is not None:
            self._brokercode = t[0]
            self._brokername = t[1]
        else:
            print("找不到此机构代码")

    @property
    def broker_code(self):
        return self._brokercode

    @property
    def broker_name(self):
        return self._brokername



if __name__ == '__main__':
    b=Broker()
