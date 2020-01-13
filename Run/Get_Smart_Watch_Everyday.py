#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zwd
# DateTime:2019/12/27-16:04
# Project:stock
# File:Get_Smart_Watch_Everyday




from urllib.request import Request,urlopen,HTTPError
import myGlobal.globalFunction as gf
import myGlobal.myTime as mt
import time





#每日收盘后或盘中获取东方财富网智能提醒所有数据，并存入数据库

def _get_smart_watch_data(url):


    for _ in range(3):
        try:
            request = Request(url)
            #此时lines已为byte格式
            lines = urlopen(request, timeout=10).read()
            if len(lines) < 100:  # no data
                return None
        except HTTPError as e:
            print(e.code)
        else:
            lines = lines.decode('utf-8')
            lines = lines.split('(')[1][:-2]

    urlPost = 'http://localhost:8080/stock/smartWatch'
    print(lines)
    try:
        status = gf.postData(lines,urlPost,flag='smart_watch')          #smart_watch标记为智能监测数据
    except:                     #如果超时，再运行两次
        for _ in range(5):
            status = gf.postData(lines, urlPost, flag='smart_watch')  # smart_watch标记为智能监测数据
    else:
        print(f"{mt.today()}智能监测数据已导入数据库")




if __name__ == '__main__':
    #1577338393
    timestamp = str(time.time())
    url = f"http://push2ex.eastmoney.com/getAllStockChanges?type=8201,8202,8193,4,32,64,8207,8209,8211,8213,8215,8204,8203,8194,8,16,128,8208,8210,8212,8214,8216&cb=jQuery1720016971080795387117_{timestamp}530&pageindex=0&pagesize=200000000&ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wzchanges&_=1577338433689"
    print(url)
    _get_smart_watch_data(url)