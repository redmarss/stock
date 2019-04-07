#!/bin/usr/env python
# -*-coding:utf-8 -*-

from urllib.request import urlopen,Request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from myGlobal.myCls.SimulateCls import BrokerSimulate
import myGlobal.myCls.msql as msql
import datetime
import myGlobal.globalFunction as gf
import myGlobal.myTime as myTime


#
def _getStock(code):
    url = "http://quote.eastmoney.com/%s.html" % code
    try:
        page = urlopen(url).read()
    except HTTPError as e:
        if e.code == 404:
            print("股票代码%s不存在" % code)
            #是否要去数据库删除该记录？

#多线程访问东方财富网，判断股票是否退市或上市，并存入数据库
def getAllStock():
    sh_list = ['sh{:0>6d}'.format(i) for i in range(600000, 604000)]         #上海股票代码，目前为从600000至603999(读者传媒)
    sz_list = ['sz{:0>6d}'.format(i) for i in range(1,2999)]            #深圳股票代码，目前从‘000001’至‘002999’
    cy_list = ['sz{:0>6d}'.format(i) for i in range(300000,300999)]     #创业板股票代码，目前从‘300000’至‘300999’
    url = "http://quote.eastmoney.com/"
    page = urlopen(url).read().decode('gbk')
    soup = BeautifulSoup(page, 'html5lib')
    links = soup.findAll('a')
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss',
                                   db='tushare', charset='utf8')
    for link in links:
        if link.text.find('(') > 0:
            pos = link.text.find('(')
            stockName = link.text[:pos]
            stockCode = link.text[pos+1:-1]
            if stockCode.startswith('30') or stockCode.startswith('60') or stockCode.startswith('00'):
                stockCode = 'sh'+stockCode if stockCode.startswith('6') else 'sz'+stockCode
                #写入数据库
                read_sql = dbObject.fetchone(field='stockname', table='stock_basic_table', where='stockcode="%s"'%stockCode)
                if read_sql is None:
                    dbObject.insert(table='stock_basic_table', stockcode=stockCode, stockname=stockName)
                else:
                    dbObject.update(table='stock_basic_table', where='stockcode="%s"'%stockCode,stockname=stockName)
                    # if getStauts(stockCode) == False:
                    #     dbObject.update(table='stock_basic_table', where='stockcode="%s"'%stockCode,status='已退市')
    dbObject.delete(table='stock_basic_table', where='stockname like "%%退%%"')

#判断股票是否退市（每判断一次都要访问一个网页，效率有点低）
def getStauts(code):
    url="http://quote.eastmoney.com/"
    if code.startswith('6'):
        url += 'sh%s.html'%code
    elif code.startswith('30') or code.startswith('00'):
        url += 'sz%s.html'%code
    page = urlopen(url).read().decode('gbk')
    soup = BeautifulSoup(page, 'html5lib')
    status = soup.find(id='price9')
    if 'data-bind' in status.attrs.keys():      #status有'data-bind'字段说明未退市，否则为已退市或停牌
        return True
    else:
        return False

#将机构代码、机构名称写入broker_info表（每月运行）
def getBrokerInfo():
    dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss',
                                   db='tushare', charset='utf8',mycursor='list')
    list_broker = dbObject.fetchall(table='broker_buy_summary', field='broker_code')
    list_broker = list(set(list_broker))

    for i in range(len(list_broker)):
        broker_code = list_broker[i][0]
        broker_name = dbObject.fetchone(table="broker_buy_summary",field="broker_name",
                                        where="broker_code='%s'"%broker_code,order="ts_date desc")[0]
        getcode = dbObject.fetchone(table='broker_info',where="broker_code='%s'"%broker_code)
        if getcode is None:
            dbObject.insert(table='broker_info',broker_code=broker_code,broker_name=broker_name)
        else:
            dbObject.update(table='broker_info',where="broker_code='%s'"%broker_code,broker_name=broker_name)

        dbObject.update(table="broker_buy_summary",broker_name=broker_name,where="broker_code='%s'"%broker_code)
        print("%s机构数据清洗完毕"%broker_code,i)

#每年运行一次即可
@gf.typeassert(str,str)
def is_holiday(startdate='2017-01-01',enddate="2019-12-31"):
    '''
            1、接口地址：http://api.goseek.cn/Tools/holiday?date=数字日期，支持https协议。
            2、返回数据：工作日对应结果为 0, 休息日对应结果为 1, 节假日对应的结果为 2
            3、节假日数据说明：本接口包含2017年起的中国法定节假日数据，数据来源国务院发布的公告，每年更新1次，确保数据最新
            4、示例：
            http://api.goseek.cn/Tools/holiday?date=20170528
            https://api.goseek.cn/Tools/holiday?date=20170528
            返回数据：
            {"code":10001,"data":2}
            注：周末无论如何股票不交易，返回1

    '''
    date = datetime.datetime.strptime(startdate, "%Y-%m-%d").date()
    enddate = datetime.datetime.strptime(enddate,"%Y-%m-%d").date()
    while date<=enddate:
        isholiday = 3

        apiUrl = "http://api.goseek.cn/Tools/holiday?date=" + str(date).replace("-","")
        request = Request(apiUrl)
        try:
            response = urlopen(request)
        except:
            raise ValueError
        else:
            response_data = response.read()
        if str(response_data)[-3] == '0':
            if date.weekday()==5 or date.weekday()==6:
                isholiday =1    #周末，无论是否工作日，都返回1
            else:
                isholiday = 0   # 工作日返回0
        else:
            isholiday = 1   # 节假日返回1

        dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss',
                                       db='tushare', charset='utf8')
        try:
            if not dbObject.fetchone(table="is_holiday", field=date, where="date='%s'"%str(date)):
                dbObject.insert(table="is_holiday", date=str(date), isholiday=str(isholiday))
                print("是否工作日%s写入数据库成功" % str(date))
            else:
                dbObject.update(table="is_holiday",where="date='%s'" % str(date), isholiday=str(isholiday))
                print("是否工作日%s更新成功" % str(date))
        except:
            raise ValueError
        date = date + datetime.timedelta(days=1)

#需重写
#每月10日模拟买入上一月数据
# @gf.typeassert((str,type(None)), (str,type(None)), int)
# def simulate_buy(startdate=None,enddate=None, amount=1000):
#     if startdate is None:
#         startdate = datetime.datetime.today().date()+datetime.timedelta(days=-60)
#     print(startdate)
#     if enddate is None:
#         enddate = datetime.datetime.today().date()
#     print(enddate)
#     dbObject = msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss', db='tushare',
#                                    charset='utf8')
#     d = dbObject.fetchall(table="broker_buy_summary", field="broker_code,ts_date",
#                           where="ts_date between '%s' and '%s' order by ts_date"%(startdate,enddate))
#     for i in range(len(d)):
#         broker_code = d[i][0]
#         ts_date = str(d[i][1])
#         b = BrokerSimulate(broker_code,ts_date)              #日期参数必须为str类型
#         b.simulate_buy(amount)




if __name__ == "__main__":
    #每月10日运行
    #getAllStock()
    _getStock("sh650000")
    #getBrokerInfo()
    #simulate_buy("simulate_buy")
    #is_holiday("2017-01-01","2019-12-31")
    print()