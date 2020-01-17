# -*- coding:utf8 -*-
import myGlobal.globalFunction as gf
from urllib.request import urlopen, Request,HTTPError
from multiprocessing import Pool        #多线程
from functools import partial
import datetime
import time
import re
import subprocess
import jpype

# region 多线程获取每日股票信息
def _getDayData(code=None,start="2017-01-01",end="2018-12-31"): #code作为多线程参数一定要放第一个
    url = 'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq2017&param=%s,day,%s,%s,640,qfq'\
          %(code,start,end)
    for _ in range(5):
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
    urlPost = 'http://localhost:8080/stock/tradeHistory'            #MVN推送地址

    status = gf.postData(textByte,urlPost,flag='stock')          #flag标记为每日股票数据
    print("%s股票从%s至%s数据导入完成"%(code,start,end))


def RunGetDayDataToMVN(start,end,stock_li=[]):
    '''
    多线程运行_getDayData
    '''
    if len(stock_li)==0:
        stock_li = gf.getStockFromTable()
    pool = Pool(30)
    pool.map(partial(_getDayData,start=start,end=end),stock_li)
    pool.close()
    pool.join()
# endregion

# region 获取机构龙虎榜信息
#根据日期取出机构交易数据并调用postData函数至数据库
def brokerInfo(startDate=None, endDate=None, pagesize=200000):
    urlPost="http://localhost:8080/broker/purchaseSummary"
    LHBYYBSBCS=f"http://datainterface3.eastmoney.com/EM_DataCenter_V3/Api//LHBYYBSBCS/GetLHBYYBSBCS?tkn=eastmoney&mkt=&dateNum=&startDateTime={startDate}&endDateTime={endDate}&sortRule=1&sortColumn=JmMoney&pageNum=1&pageSize={pagesize}&cfg=lhbyybsbcs"
    try:
        request=Request(LHBYYBSBCS)
        text=urlopen(request).read()                     #type is byte
        gf.postData(text,urlPost,flag='lhb')
    except Exception as e:
        print(e)
# endregion

if __name__ == '__main__':
    #运行jvm虚拟机
    #调用jar文件
    jvmPath = r'C:\Program Files\Java\jdk1.8.0_171\jre\bin\server\jvm.dll'
    jpype.startJVM(jvmPath,"-Djava.class.path=H:\\github\\siteminder\\target\\siteminder-0.0.1-SNAPSHOT.jar") 
    jpype.java.lang.System.out.println("hello world!")
    jpype.shutdownJVM()
    print("test")



    if datetime.datetime.today().hour > 18:     #运行时间大于18点
        start = str(datetime.datetime.today().date()-datetime.timedelta(days=360))
    else:
        start = str(datetime.datetime.today().date() - datetime.timedelta(days=361))

    end = str(datetime.datetime.today().date() + datetime.timedelta(days=1))


    #每日获取股票相关数据
    RunGetDayData(start=start,end=end)
    #每日获取机构数据
    brokerInfo(startDate=start,endDate=end)
