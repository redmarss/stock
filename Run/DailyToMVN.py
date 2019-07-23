#!/usr/bin/env python
# -*- coding:utf8 -*-
import myGlobal.globalFunction as gf
from urllib.request import urlopen, Request,HTTPError
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import datetime
import re


def _getDayData(code=None,start="2017-01-01",end="2018-12-31"): #code作为多线程参数一定要放第一个
    url = 'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq2017&param=%s,day,%s,%s,640,qfq'\
          %(code,start,end)
    for _ in range(3):
        try:
            request = Request(url)
            lines = urlopen(request, timeout=10).read()
            if len(lines) < 100:  # no data
                return None
        except HTTPError as e:
            print(e.code)
        else:
            lines = lines.decode('utf-8')
            lines = lines.split('=')[1]
            reg = re.compile(r',{"nd.*?}')
            lines = re.subn(reg, '', lines)
            reg = re.compile(r',"qt":{.*?}')
            lines = re.subn(reg, '', lines[0])
            reg = r',"mx_price".*?"version":"4"'
            lines = re.subn(reg, '', lines[0])
            reg = r',"mx_price".*?"version":"12"'
            lines = re.subn(reg, '', lines[0])
            # 将str格式转换成byte
            textByte = bytes(lines[0], encoding='utf-8')
    urlPost = 'http://localhost:8080/stock/tradeHistory'
    status = gf.postData(textByte,urlPost,flag='stock')          #flag标记为每日股票数据
    # if status == 500:
    #     sql = "update tushare.stock_basic_table set tui_flag='1' where stockcode = '%s'" %code
    #     DBHelper().execute(sql)
    #     print("%s或已退市,已标记"%code)
    # else:
    print("%s股票从%s至%s数据导入完成"%(code,start,end))


def RunGetDayData(start="2017-01-01",end="2019-04-15",stock_li=[]):
    '''

    :param stock_list:需要运行的股票列表
    :param date:开始日期
    :param filetype:文件格式
    :param count:往前倒数的天数
    :return:
    '''
    if len(stock_li)==0:
        stock_li = gf.getAllStockFromTable()
    mapfunc = partial(_getDayData,start=start,end=end)
    pool = ThreadPool(10)        #3个线程分别对应front,back,no
    pool.map(mapfunc,stock_li)       #会将list_fq参数放在_getDayData参数拦最左边
    pool.close()                    #关闭进程池，不再接受新的进程
    pool.join()                     #主进程阻塞等待子进程的退出


#根据日期取出机构交易数据并调用postData函数至数据库
def brokerInfo(startDate=None, endDate=None, pagesize=200000):
    urlPost="http://localhost:8080/broker/purchaseSummary"
    LHBYYBSBCS="http://datainterface3.eastmoney.com/EM_DataCenter_V3/Api//LHBYYBSBCS/GetLHBYYBSBCS?tkn=eastmoney&mkt=&dateNum=&startDateTime=%s&endDateTime=%s&sortRule=1&sortColumn=JmMoney&pageNum=1&pageSize=%s&cfg=lhbyybsbcs"
    try:
        request=Request(LHBYYBSBCS%(startDate,endDate,pagesize))
        text=urlopen(request, timeout=10).read()                     #type is byte
        gf.postData(text,urlPost,flag='lhb')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    if datetime.datetime.today().hour > 18:     #运行时间大于18点
        start = str(datetime.datetime.today().date()-datetime.timedelta(days=37))
        end = str(datetime.datetime.today().date() + datetime.timedelta(days=1))


    else:
        start = str(datetime.datetime.today().date() - datetime.timedelta(days=38))
        end = str(datetime.datetime.today().date())

    #everyday = start.replace("-","")
    #每日获取股票相关数据
    #RunGetDayData(start="2019-01-01",end=end)
    #每日获取机构数据
    brokerInfo("2017-01-01","2017-01-10")