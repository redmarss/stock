#!/bin/usr/env python
# -*-coding:utf-8 -*-

#数据库操作类
import pymysql
import pandas as pd
from sqlalchemy import create_engine
import myGlobal.myCls.mylogger as mylogger
#屏蔽Warning警告
# from warnings import filterwarnings
# filterwarnings('ignore',category=pymysql.Warning)



class DBHelper(object):
    # 构造函数
    def __init__(self):
        #连接数据库
        try:
            self.conn = pymysql.connect(
                host='cdb-iar6zzqb.gz.tencentcdb.com',
                port=10141,
                db='tushare',
                user='root',
                passwd='888@XyFxBm',
                charset='utf8'
            )

        except:
            mylogger.mylogger().error("connectDatabase failed")

        self.cur = self.conn.cursor()



    # 关闭数据库
    def close(self):
        # 如果数据打开，则关闭；否则没有操作
        if self.conn and self.cur:
            self.cur.close()
            self.conn.close()
        return True

    # 执行数据库的sq语句,主要用来做插入操作
    def execute(self, sql, params=None):
        # 连接数据库
        try:
            #执行sql，提交操作
            self.cur.execute(sql, params)
            self.conn.commit()
        except:
            mylogger.mylogger().error("execute failed: " + sql)
            if params is not None:
                mylogger.mylogger().error("params: " + params)
            self.close()
            return False
        return True

    # 用来查询表数据
    def fetchall(self, sql, params=None):
        self.execute(sql, params)       #包含try语句，有错误则会记录
        result = self.cur.fetchall()
        self.close()                #关闭连接，否则多线程操作时会超过最大连接数
        return result

    # 获取一条数据
    def fetchone(self,sql,params=None):
        self.execute(sql,params)    #包含try语句，有错误则会记录
        result = self.cur.fetchone()
        self.close()                #关闭连接，否则多线程操作时会超过最大连接数
        return result

    def isTableExists(self, tablename):
        sql = "show tables;"
        t = self.fetchall(sql)
        li_table = [str(i[0]) for i in t]
        if tablename in li_table:
            return True
        else:
            return False

