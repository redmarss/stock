#!/bin/usr/env python
# -*- coding:utf-8 -*-

import pymysql
#from myGlobal.myCls.mylogger import mylogger
import sys




class DBHelper:
    # 构造函数
    def __init__(self, host='127.0.0.1', user='root', pwd='redmarss', db='tushare'):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        self.conn = None
        self.cur = None
        self.isConnect = self.connectDatabase()



    # 连接数据库
    def connectDatabase(self):
        try:
            self.conn = pymysql.connect(self.host, self.user,
                                        self.pwd, self.db, charset='utf8')
        except:
            #mylogger().error("connectDatabase failed")
            return False
        self.cur = self.conn.cursor()
        return True

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
        if self.isConnect is False:
            self.connectDatabase()
        try:
            if self.conn and self.cur:
                # 正常逻辑，执行sql，提交操作
                self.cur.execute(sql, params)
                self.conn.commit()
        except:
            #mylogger().error("execute failed: " + sql)
            #mylogger().error("params: " + params)
            self.close()
            return False
        return True

    # 用来查询表数据
    def fetchall(self, sql, params=None):
        #self.connectDatabase()
        self.execute(sql, params)
        return self.cur.fetchall()


if __name__ == '__main__':
    pass