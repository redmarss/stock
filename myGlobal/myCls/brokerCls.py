#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.mysqlCls as msql

class Broker(object):
    _brokercode = None
    _brokername = None
    _buylist = None

    # 构造函数，如果ts_date不为None,则返回当日该机构买入的股票列表至_buylist
    def __init__(self, broker_code, ts_date = None):
        dbObject = msql.SingletonModel(host='localhost', port='3306',
                                       user='root', passwd='redmarss',
                                       charset='utf8',db='tushare', mycursor='list')
        # 先获得机构名称及机构代码
        broker_info = dbObject.fetchone(table='broker_info', field='broker_code,broker_name', where="broker_code='%s'" % (broker_code))
        if broker_info is not None:
            self._brokercode = broker_info[0]
            self._brokername = broker_code[1]
        else:
            print("找不到该机构代码对应的机构")
            return

        #如果传入参数中包含ts_date，则返回buy_list
        if ts_date is not None:
            t_broker_buy = dbObject.fetchall(table='broker_buy_stock_info as a,broker_buy_summary as b', field='a.stock_code',
                                        where='a.broker_buy_summary_id=b.id and b.broker_code="%s" and b.ts_date="%s"' % (broker_code, ts_date))
            if len(t_broker_buy) != 0:                       #tbroker长度为0，说明找不到对应的数据
                self._buylist = [item[0][:6] for item in t_broker_buy]
            else:
                print("该机构当天没有买卖股票")
        else:
            self._buylist = None

    @property
    def broker_code(self):
        return self._brokercode

    @property
    def broker_name(self):
        return self._brokername



if __name__ == '__main__':
    #b=Broker('80467525')
    b=Broker('80467525','2018-06-22')
