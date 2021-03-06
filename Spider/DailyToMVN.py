# -*- coding:utf8 -*-
import sys
sys.path.append("H:\\python\\stock\\")
import myGlobal.globalFunction as gf

from urllib.request import urlopen, Request,HTTPError
from multiprocessing import Pool        #多线程
from functools import partial
import lxml.etree as etree

import myGlobal.myTime as mTime

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
    #stock_li =['sz300790']
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

# region 每日清洗broker_info中数据
def BrokerInfoClean(startdate,enddate):

    #取出broker_buy_summary表中所有存在的broker_code 并去重
    sql_select = f"select broker_code,broker_name from broker_buy_summary where ts_date between '{startdate}' and '{enddate}'"
    list_broker = DBHelper().fetchall(sql_select)
    list_broker = list(set(list_broker))

    for i in range(len(list_broker)):
        code = list_broker[i][0]
        name = list_broker[i][1]


        #查找该code 是否在broker_info表
        code_sql = f"select * from broker_info where broker_code='{code}'"
        t = DBHelper().fetchall(code_sql)
        if len(t) > 0 : # code在broker_info表中
            #判断broker_info中机构名称是否与name一致，如果不一致，则更新名称并数据清洗
            is_samename_sql = f"select broker_name from broker_info where broker_code='{code}'"
            old_name = DBHelper().fetchone(is_samename_sql)[0]

            if old_name != name:
                print(f"正清洗机构代码{code}数据")
                #更新broker_info表中机构名称
                update_name_sql = f"update broker_info set broker_name='{name}' where broker_code='{code}'"
                DBHelper().execute(update_name_sql)
                #更新broker_buy_summary中历史数据
                update_broker_buy_summay_sql = f'update broker_buy_summary set broker_name="{name}" where broker_code="{code}"'
                DBHelper().execute(update_broker_buy_summay_sql)
                print(f"机构代码{code}数据清洗成功")

        else:
            #插入该机构代码及名称至broker_info表
            insert_broker_sql = f'insert into broker_info (broker_code,broker_name) VALUES ("{code}","{name}")'
            DBHelper().execute(insert_broker_sql)
# endregion

def CleanMVN(strdate):
    #删除龙虎榜买卖数据中所有B股（股票代码以‘2’‘9’开头）
    select_sql = f'''
    SELECT a.id,b.id,a.stock_code FROM
    broker_buy_stock_info AS a
        INNER JOIN
    broker_buy_summary AS b ON a.broker_buy_summary_id = b.id
    where (a.stock_code like '2%' or a.stock_code like '9%') and ts_date <'{strdate}'
    '''
    t_sql = DBHelper().fetchall(select_sql)

    for i in range(len(t_sql)):
        broker_buy_stock_info_id =t_sql[i][0]
        broker_buy_summary_id = t_sql[i][1]
        stock_code = t_sql[i][2]
        del_broker_buy_stock_info = f'''
        delete from broker_buy_stock_info where id="{broker_buy_stock_info_id}";
        '''
        del_broker_buy_summary = f'''
        delete from broker_buy_summary where id = "{broker_buy_summary_id}"; 
        '''

        try:
            DBHelper().execute(del_broker_buy_stock_info)
            DBHelper().execute(del_broker_buy_summary)
            print(f"删除{strdate}日股票代码为{stock_code}龙虎榜数据成功！")
        except:
            print("删除数据错误")


#获取每日热门股吧股票
def GetHotBar(tablename='hotbar'):
    url = "http://guba.eastmoney.com/remenba.aspx?type=1"
    li_stock=[]
    for _ in range(3):      #为防止网络延迟，运行3次
        try:
            request = Request(url)
            lines = urlopen(request, timeout=10).read()
        except HTTPError as e:
            print("读取热门股吧错误")
        else:
            lines = lines.decode('utf-8')

            reg = re.compile(r'<ul class="list clearfix">.*?</ul>')     #用正则表达式找出热门股吧这列
            lines = reg.findall(lines)
            lines = lines[0].split('.html">')       #将含有股票姓名、股票代码这一列分离出来
            lines = lines[1:]
            for i in range(len(lines)):
                temp = str(lines[i]).split('吧')[0]
                if temp not in li_stock:
                    li_stock.append(temp)

    date =  mTime.Today()       #记录时间
    if mTime.get_hour() < 12:       #上午
        time = "08:30:00"
    elif mTime.get_hour()<18:
        time = "15:30:00"
    else:
        time = "20:30:00"

    #创建表
    create_table_sql = f'''
        CREATE TABLE `tushare`.`{tablename}` (
          `id` INT NOT NULL AUTO_INCREMENT,
          `date` VARCHAR(45) NOT NULL,
          `time` VARCHAR(45) NOT NULL,
          `stockcode` VARCHAR(45) NOT NULL,
          `stockname` VARCHAR(45) NOT NULL,
          `is_simulate` VARCHAR(45) NULL DEFAULT 0,
          PRIMARY KEY (`id`),
          UNIQUE INDEX `index2` (`date` ASC, `time` ASC,`stockcode` ASC));
    '''
    if not DBHelper().isTableExists(tablename):
        try:
            DBHelper().execute(create_table_sql)
            print(f"创建{tablename}表成功")
        except:
            print(f"创建{tablename}表失败")

    for i in range(len(li_stock)):
        stockcode = gf.code_to_symbol(li_stock[i].split(')')[0][1:])
        stockname = li_stock[i].split(')')[1]
        insert_sql = f'''
            insert into {tablename} (date,time,stockcode,stockname) VALUES ('{date}','{time}','{stockcode}','{stockname}')
        '''
        DBHelper().execute(insert_sql)
    print("收集热门股吧数据完成")






if __name__ == '__main__':
    proc = subprocess.Popen("C:\\Users\\hpcdc\\Desktop\\runjar.bat",creationflags=subprocess.CREATE_NEW_CONSOLE)
    pobj = psutil.Process(proc.pid)
    time.sleep(20)

    #运行时间为每天8.30分
    start = mTime.DateAddOrDiffDay(mTime.Today(),-21)
    #start = '2017-01-01'
    end = mTime.DateAddOrDiffDay(mTime.Today(),-1)


    #每日获取股票相关数据
    RunGetDayDataToMVN(start=start,end=end)
    #每日获取机构数据
    brokerInfo(startDate=start,endDate=end)
    #清洗当日龙虎榜、股票数据
    CleanMVN(end)
    #每日清洗broker_info表中数据
    BrokerInfoClean(startdate=start,enddate=end)
    #收集热门股吧数据并入库
    GetHotBar('hotbar')


    for c in pobj.children(recursive=True):
        c.kill()
    pobj.kill()

