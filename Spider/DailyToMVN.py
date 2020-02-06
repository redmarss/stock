# -*- coding:utf8 -*-
import sys
sys.path.append("H:\\python\\stock\\")
import myGlobal.globalFunction as gf

from urllib.request import urlopen, Request,HTTPError
from multiprocessing import Pool        #多线程
from functools import partial

import datetime
import time
import re
import subprocess,psutil

from myGlobal.myCls.msql import DBHelper




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

#每日清洗broker_info中数据
def BrokerInfoClean(startdate,enddate):
    startdate = '2017-01-01'
    enddate = str(datetime.datetime.today().date())


    #取出broker_buy_summary表中所有存在的broker_code 并去重
    sql_select = f"select broker_code,broker_name from broker_buy_summary where ts_date between '{startdate}' and '{enddate}'"
    list_broker = DBHelper().fetchall(sql_select)
    list_broker = list(set(list_broker))

    for i in range(len(list_broker)):
        # code = list_broker[i][0]
        # name = list_broker[i][1]

        code = '80561011'
        name = '南京证券股份有限公司江阴澄杨路证券营业部'

        #查找该code 是否在broker_info表
        code_sql = f"select * from broker_info where broker_code='{code}'"
        t = DBHelper().fetchall(code_sql)
        if len(t) > 0 : # code在broker_info表中
            #判断broker_info中机构名称是否与name一致，如果不一致，则更新名称并数据清洗
            is_samename_sql = f"select broker_name from broker_info where broker_code='{code}'"
            old_name = DBHelper().fetchone(is_samename_sql)[0]

            if old_name != name:
                #更新broker_info表中机构名称
                update_name_sql = f"update broker_info set broker_name='{name}' where broker_code='{code}'"
                DBHelper().execute(update_name_sql)
                #更新broker_buy_summary中历史数据
                # TODO


        else:
            #插入该机构代码及名称至broker_info表
            insert_broker_sql = f'insert into broker_info (broker_code,broker_name) VALUES ("{code}","{name}")'
            DBHelper().execute(insert_broker_sql)





if __name__ == '__main__':
    # proc = subprocess.Popen("C:\\Users\\hpcdc\\Desktop\\runjar.bat",creationflags=subprocess.CREATE_NEW_CONSOLE)
    # pobj = psutil.Process(proc.pid)
    # time.sleep(20)
    #

    if datetime.datetime.today().hour > 18:     #运行时间大于18点
        start = str(datetime.datetime.today().date()-datetime.timedelta(days=20))
    else:
        start = str(datetime.datetime.today().date() - datetime.timedelta(days=21))

    end = str(datetime.datetime.today().date() + datetime.timedelta(days=1))


    #每日获取股票相关数据
    #RunGetDayDataToMVN(start=start,end=end)
    #每日获取机构数据
    #brokerInfo(startDate=start,endDate=end)
    #每日清洗broker_info表中数据
    BrokerInfoClean(start,end)

    # for c in pobj.children(recursive=True):
    #     c.kill()
    # pobj.kill()