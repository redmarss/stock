# -*- coding:utf8  -*-
from myGlobal.myCls.BrokerCls import Broker
from myGlobal.myCls.StockCls import Stock

#多线程模拟每日机构买卖股票
def DailySimulate(brokercode,startdate,type):
    pass

#获取模拟机构的买入价及卖出价并计算盈利
def _getPrice(brokercode,date,type=1):
    b = Broker(brokercode,date)
    li_stock = b.getBuyStock()            #获取机构当天买入股票列表，存入list
    if len(li_stock)>0:
        for code in li_stock():
            s = Stock(code,date)



if __name__ =='__main__':
    s = Broker("80032251","2019-03-20")
    s.Simulate("test123456")
    print()

