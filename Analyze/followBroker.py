#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.mysqlCls as msql
import myGlobal.myCls.StockCls as mstock
import myGlobal.globalFunction as gf

#输入机构代码，日期，返回元组
#（broker_code,ts_date,[stock_list]）
def getStockCode(broker_code = None,ts_date = None):
    dbObject = msql.SingletonModel(host='localhost',port='3306',user='root',passwd='redmarss',db='tushare',charset='utf8')
    d = dbObject.fetchall(table='broker_buy_stock_info as a,broker_buy_summary as b',
                          field='a.stock_code',
                          where='a.broker_buy_summary_id=b.id and b.broker_code="%s" and b.ts_date="%s"' % (broker_code, ts_date))
    wantbuy_list = [item['stock_code'][:6] for item in d]
    return broker_code, ts_date, wantbuy_list


def buy_stock(t,amount = 1000):
    #判断传入参数是否合规
    if not isinstance(t, tuple) or not isinstance(t[2], list):
        print("传入参数有误")
        return

    #根据模拟的参数进行买入
    ts_date = t[1]
    broker_code = t[0]
    wantbuy_list = t[2]
    for i in range(len(wantbuy_list)):
        stock = mstock.Stock(wantbuy_list[i], ts_date)
        stock_next = stock.next_someday_price(1)
        stock_next2day = stock.next_someday_price(2)
        buy_price = stock_next.open_price
        stock_code = stock.code
        sell_price = (stock_next2day.high_price+stock_next2day.low_price)/2
        gainmoney = round((sell_price-buy_price)*amount,2)
        gainpercent = round((sell_price*amount-buy_price*amount)/(buy_price*amount),4)
        #如果第二天开盘涨幅小于5%，则买入
        if gf.ChangeRange(stock.close_price,stock_next.open_price) <0.05:
            #模拟买入并写入数据库
            dbObject = msql.SingletonModel(host='localhost',port='3306',user='root',
                                           passwd='redmarss',db='tushare',charset='utf8')
            dbObject.insert(table='simulate_buy',ts_date=ts_date,broker_code=broker_code,
                                  stock_code=stock_code,buy_price=buy_price,sell_price=sell_price,
                                  amount=amount,gainmoney=gainmoney,gainpercent=gainpercent)




if __name__ =='__main__':
    dbObject = msql.SingletonModel(host='localhost',port='3306',user='root',passwd='redmarss',db='tushare',charset='utf8')
    d = dbObject.fetchall(table="broker_buy_summary", field="broker_code,ts_date", where="ts_date<='2017-12-31'")
    for i in range(len(d)):
        t=getStockCode(d[i]['broker_code'],str(d[i]['ts_date']))
        buy_stock(t,1000)



