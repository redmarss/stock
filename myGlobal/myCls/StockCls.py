#!/bin/usr/env python
# -*- coding:utf-8 -*-
import myGlobal.myCls.msql as msql
import myGlobal.globalFunction as gf
import myGlobal.myTime as myTime
import datetime
import pandas as pd
from decimal import Decimal



#Stock类
#输入股票代码，日期作为参数
class Stock(object):
    @gf.typeassert(code=str, ts_date=str)
    def __init__(self, code, ts_date):
        if gf.isStockA(code) is not True:
            print("%s不是沪深A股" % code)
            self._ts_date = None
            self._code = None
            return
        #股票代码标准化
        code = gf.code_to_symbol(code)
        #判断参数合规性
        if not gf.is_tradeday(code, ts_date):                   #可能返回None,True,False
            print("%s在%s未查询到交易记录" % (code, ts_date))
            self._ts_date = None
            self._code = None
            return
        #创建数据库对象（单例模式）
        self._dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss',
                                            db='tushare', charset='utf8')
        # 获取股票当日交易信息
        self.__tuplestock = self._dbObject.fetchone(table='stock_trade_history_info',
                                                  where='stock_code="%s" and ts_date="%s"' % (code, ts_date))
        self._ts_date = ts_date
        self._code = code

    @property
    def code(self):
        return self._code

    @property
    def ts_date(self):
        return self._ts_date

    @property
    def open_price(self):
        if self.__tuplestock is not None:
            return float(self.__tuplestock[3])
        else:
            return None

    @property
    def close_price(self):
        if self.__tuplestock is not None:
            return float(self.__tuplestock[4])
        else:
            return None

    @property
    def high_price(self):
        if self.__tuplestock is not None:
            return float(self.__tuplestock[5])
        else:
            return None

    @property
    def low_price(self):
        if self._tuplestock is not None:
            return float(self._tuplestock[6])
        else:
            return None

    @property
    def volume(self):
        if self._tuplestock is not None:
            return float(self._tuplestock[7])
        else:
            return None


    #根据输入参数（code,ts_date）返回下一个(或多个)交易日的数据存入Stock类
    @gf.typeassert(days=int)
    def next_some_days(self, days=7):
        '''
            参数示例：7，‘7’，‘7s'
            返回类型：list,list,None
            len(list)应等于days，list中每个元素应为Stock类型
        '''
        if self._code is None:
            return
        stocklist=[]
        i = 0
        date = self._ts_date         #str类型
        #当stocklist函数长度小于days且数据库中有数据
        while len(stocklist) < days:
            if gf.is_tradeday(str(self._code), str(date)):
                s = Stock(self._code, date)
                stocklist.append(s)
            date = myTime.diffDay(date, 1)
            # 如果日期最终大于”今天”，则中断循环，否则死循环
            if datetime.datetime.strptime(date, "%Y-%m-%d").date() > datetime.datetime.today().date():
                break
        return stocklist

    #计算买入卖出策略，stype为各种策略编号
    #返回ts_date,broker_code,stock_code,buy_date,sell_date,buy_price,sell_price,amount,gainmoney,gainpercent
    @gf.typeassert(broker_code=str, amount=int, ftype=int)
    def strategy(self, broker_code, amount, ftype):
        if self._ts_date is None:
            return
        #第一种策略:第二天开盘买，第三天开盘卖
        if ftype == 1:
            return self.__strategy1(broker_code,amount)


    #实现第一种策略:第二天开盘买，第三天开盘卖
    def __strategy1(self, broker_code, amount):
        dict1 = {}
        price_list = self.next_some_days(3)
        if len(price_list) != 3:
            return
        #第二天开盘涨幅超过8%，不买了
        if gf.ChangeRange(price_list[0].close_price, price_list[1].open_price) > 0.08:
            return
        dict1['ts_date'] = self._ts_date
        dict1['broker_code'] = broker_code
        dict1['stock_code'] = self._code
        dict1['buy_date'] = myTime.diffDay(self._ts_date, 1)
        dict1['sell_date'] = myTime.diffDay(self._ts_date, 2)
        dict1['buy_price'] = price_list[1].open_price
        dict1['sell_price'] = price_list[2].open_price
        dict1['amount'] = amount
        dict1['gainmoney'] = round((dict1['sell_price'] - dict1['buy_price']) * amount, 2)
        dict1['gainpercent'] = round(dict1['gainmoney']/(dict1['buy_price']*amount), 2)
        dict1['ftype'] = '1'
        return dict1

    @gf.typeassert(days=int)
    def getStockInfo(self, days=7):
        '''
        获取某股票N个交易日内的所有数据,返回元组
        :param code: 股票代码
        :param startdate: 开始日期
        :param days: 天数
        :return: 股票交易信息（元组）
        '''
        code = self._code
        if code is None:
            return
        field_list = ["a.id", "a.stock_code", "a.ts_date", "a.open_price", "a.close_price", "a.high_price",
                      "a.low_price", "a.volume", "b.k", "b.d", "b.j"]
        field = ""
        for i in field_list:
            field += "%s," % i
        field = field.rstrip(",")
        t = self._dbObject.fetchall(table='stock_trade_history_info as a,qualification as b',
                                    field=field,
                                    where="a.stock_code=b.stock_code and a.ts_date=b.ts_date and "
                                          "a.stock_code='%s' and a.ts_date%s='%s' order by a.ts_date desc"
                                          % (code, ('>' if days > 0 else '<'), self._ts_date),
                                    limit=str(abs(days)))

        return pd.DataFrame(list(t),columns=field_list)

    #计算均线价格
    @gf.typeassert(days=int)
    def MA(self, days=5):
        '''
            参数示例：5
            返回类型：float,float,None
        '''
        if days not in [5,10,15,20,30,60,120,250,360]:
            print("MA参数不符合定义")
            return
        list_MA=[]
        t_MA = self.getStockInfo(0-days)
        if len(t_MA)>=days:
            for i in range(len(t_MA)):
                list_MA.append(t_MA[i][4])          #收盘价
            s = pd.Series(list_MA)
            return round(s.mean(), 2)
        else:                                       #数据不足，返回0.0
            return 0.0


    def getMA(self,*args):
        for i in args:
            ma = self.MA(i)
            field = "MA"+str(i)
            self._writeQualifi(field=ma)


    @gf.typeassert(N=int)
    def KDJ(self, N=9):
        if N < 0:
            print("N值不能为负数")
            return
        t_stock = None
        if self._code is not None and self._ts_date is not None:
            df_stock = self.getStockInfo(0-N)
            #寻找N日内收盘价
            if df_stock.shape[0] < N:
                k = d = 50
                j = 3 * k - 2 * d
                self._writeQualifi(k=k,d=d,j=j)
            else:
                #n日RSV=（Cn－Ln）/（Hn－Ln）×100
                Cn = Decimal.from_float(self.close_price)                     #当日收盘价
                Ln = df_stock["a.low_price"].min()                            #N日最低价
                Hn = df_stock["a.high_price"].max()                           #N日最高价
                Rsv = (Cn-Ln)/(Hn-Ln)*100
                #获取前一日K值与D值
                k_last = df_stock.loc[1, "b.j"]           #前一日K值
                d_last = df_stock.loc[1, "b.d"]           #前一日D值
                #当日K值=2/3×前一日K值+1/3×当日RSV
                k = round(Decimal.from_float(2/3)*k_last+Decimal.from_float(1/3)*Rsv,2)
                d = round(Decimal.from_float(2/3)*d_last+Decimal.from_float(1/3)*k,2)
                j = 3*k-2*d

                self._writeQualifi(k=k, d=d, j=j)


    def _writeQualifi(self,**kwargs):
        for key,value in kwargs.items():
            #先判断qualification表中是否有k列，如果没有则添加
            try:
                #如果原来就有这列，则pass
                t = self._dbObject.fetchall(table="qualification",field=key)
            except:
                #没有这一列，则添加
                sql = '''
                ALTER TABLE `tushare`.`qualification` 
                ADD COLUMN `%s` VARCHAR(45) NULL;
                '''%key
                self._dbObject.execute(sql)
            #开始写入
            stock_code = self._code
            ts_date = self._ts_date
            t = self._dbObject.fetchall(table="qualification",
                                        where="stock_code='%s' and ts_date='%s'" % (stock_code,ts_date))

            if len(t) == 0:
                self._dbObject.insert(table="qulification",stock_code=stock_code,ts_date=ts_date,key=value)
                print("%s(%s)记录成功" % (stock_code, ts_date))
            else:
                self._dbObject.update(table="qualification",where="stock_code='%s' and ts_date='%s'"%(stock_code,ts_date),
                                      eval(key)=value)
                print("%s(%s)更新成功" % (stock_code, ts_date))
        # #取出参数中的技术指标
        # k = kwargs['k']
        # d = kwargs['d']
        # j = kwargs['j']
        #
        # stock_code = self._code
        # ts_date = self._ts_date
        #
        # t = self._dbObject.fetchall(table="qualification",
        #                             where="stock_code='%s' and ts_date='%s'"%(stock_code,ts_date))
        # if len(t) == 0:
        #     self._dbObject.insert(table="qualification",stock_code=stock_code,ts_date=ts_date,
        #                           k=k, d=d, j=j)
        #     print("%s(%s)记录成功"%(stock_code,ts_date))
        # else:
        #     self._dbObject.update(table="qualification",where="stock_code='%s' and ts_date='%s'"%(stock_code,ts_date),
        #                           k=k,d=d,j=j)
        #     print("%s(%s)更新成功" % (stock_code, ts_date))




if __name__ == "__main__":
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss',
                                db='tushare', charset='utf8')
    t = dbObject.fetchall(table="stock_trade_history_info",field="stock_code,ts_date",
                         where="ts_date<'%s' order by stock_code,ts_date "%("2017-01-31"))
    for i in range(len(t)):
        code = t[i][0]
        date = str(t[i][1])
        s = Stock(code, date)
        s.KDJ()


