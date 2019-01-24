#!/bin/usr/env python
# -*-coding:utf-8 -*-

#数据库操作类
import pymysql
import pandas as pd
from sqlalchemy import create_engine
#屏蔽Warning警告
# from warnings import filterwarnings
# filterwarnings('ignore',category=pymysql.Warning)

class SingletonModel:
    #数据库连接对象
    __db = None
    #游标对象
    __cursor = None

    __strEngine = None


    def __new__(self, *args, **kwargs):
        if not hasattr(self,'_instance'):
            self._instance = super().__new__(self)
            host = 'host' in kwargs and kwargs['host'] or 'localhost'
            port ='port' in kwargs and kwargs['port'] or '3306'
            user ='user' in kwargs and kwargs['user'] or 'root'
            passwd ='passwd' in kwargs and kwargs['passwd'] or '123456'
            db = 'db' in kwargs and kwargs['db'] or 'test'
            charset = 'charset' in kwargs and kwargs['charset'] or 'utf8'

            #打开数据库连接
            #print('连接数据库')
            self.__db = pymysql.connect(host=host,port=int(port),user=user,passwd=passwd,db=db,charset=charset)

            #创建一个游标对象
            #self.__cursor = self.__db.cursor(cursor=pymysql.cursors.DictCursor)  # 返回值为字典形式
            self.__cursor = self.__db.cursor()  # 返回值为列表形式



            self.__strEngine =  "mysql+pymysql://" + user + ':' + passwd + '@' + host + ':' + str(
            port) + '/' + db + '?charset=' + charset
        return self._instance

    #返回执行execute()方法后影响的行数
    def execute(self,sql):
        self.__cursor.execute(sql)
        data = self.__cursor.fetchall()
        return data

    #增->返回新增ID
    def insert(self,**kwargs):
        table=kwargs['table']       #取出参数中table名称
        kwargs.pop('table')         #将参数中table删除，方便后续操作
        sql = 'insert into %s set '%table
        for k,v in kwargs.items():
            sql += "%s='%s',"%(k,v)
        sql=sql.rstrip(',')
        #print(sql)
        try:
            #执行SQL语句
            self.__cursor.execute(sql)
            self.__db.commit()
            res = self.__cursor.lastrowid   #获取最后一行自增id
        except:
            #发生错误时回滚
            self.__db.rollback()
        return res

    #删->返回影响的行数
    def delete(self,**kwargs):
        table = kwargs['table']
        where = kwargs['where']
        sql = 'delete from %s where %s'%(table,where)
        #print(sql)
        try:
            self.__cursor.execute(sql)
            self.__db.commit()
            rowcount = self.__cursor.rowcount   #返回影响的行数
        except:
            #发生错误时回滚
            self.__db.rollback()
        return rowcount

    #改->返回影响的行数
    def update(self,**kwargs):
        #表名称
        table = kwargs['table']
        kwargs.pop('table')

        #where条件
        where = kwargs['where']
        kwargs.pop('where')

        sql = 'update %s set '%table
        for k,v in kwargs.items():
            sql += "%s='%s',"%(k,v)
        sql = sql.rstrip(',')
        sql += ' where %s'%where
        #print(sql)
        try:
            self.__cursor.execute(sql)
            self.__db.commit()
            rowcount = self.__cursor.rowcount
        except:
            self.__db.rollback()
        return rowcount

    #查->单条数据
    def fetchone(self,**kwargs):
        table = kwargs['table']
        #字段
        field = 'field' in kwargs and kwargs['field'] or '*'

        #where条件
        where = 'where' in kwargs and 'where '+kwargs['where'] or ''

        #order条件
        order = 'order' in kwargs and 'order by '+kwargs['order'] or ''

        sql = 'select %s from %s %s %s limit 1'%(field,table,where,order)
        #print(sql)
        try:
            self.__cursor.execute(sql)
            data=self.__cursor.fetchone()
        except:
            self.__db.rollback()
        return data

    #查->多条数据
    def fetchall(self,**kwargs):
        table = kwargs['table']
        #字段
        field = 'field' in kwargs and kwargs['field'] or '*'
        #where条件
        where = 'where' in kwargs and 'where '+kwargs['where'] or ''
        #order
        order = 'order' in kwargs and 'order by '+kwargs['order'] or ''
        #limit
        limit = 'limit' in kwargs and 'limit '+kwargs['limit'] or ''


        sql = 'select %s from %s %s %s %s'%(field,table,where,order,limit)
        #print(sql)

        try:
            self.__cursor.execute(sql)
            data = self.__cursor.fetchall()
        except:
            self.__db.rollback()
        return data

    #删->删除整张表数据
    def truncate(self,**kwargs):
        table = kwargs['table']
        sql = 'truncate table %s'%table
        try:
            self.__cursor.execute(sql)
            self.__db.commit()
            rowcount = self.__cursor.rowcount   #返回影响的行数
        except:
            #发生错误时回滚
            self.__db.rollback()
        return rowcount

    def dropTable(self,**kwargs):
        table = kwargs['table']
        sql = 'drop table %s' % table
        try:
            self.__cursor.execute(sql)
            self.__db.commit()
            print("删除表%s成功"%table)
        except:
            #发生错误时回滚
            self.__db.rollback()

    # 将一个DataFrame存入mysql的table表中
    def DataframeToSql(self,df, table):


        engine = create_engine(self.__strEngine)
        try:
            pd.io.sql.to_sql(df, table, engine, if_exists='append')
            #print("成功")
            engine.dispose()
        except:
            print("重复")
            engine.dispose()


    def isTableExists(self, **kwargs):
        table = kwargs["table"]
        sql = "show tables;"
        t = self.execute(sql)
        li_table = [str(i[0]) for i in t]
        if table in li_table:
            return True
        else:
            return False

    #析构函数
    def __del__(self):
        #关闭数据库连接
        self.__db.close()
        #print('关闭数据库连接')

#主函数
# if __name__ == '__main__':
#     dbObject = SingletonModel(host="localhost", port=3306, user="root", passwd="redmarss", db="test", charset="utf8")

# 创建表
#     print("创建表")
#     sql = "drop table if exists user"
#     dbObject.execute(sql)
#     sql='''CREATE TABLE `user` (
#     `id` int(11) NOT NULL AUTO_INCREMENT,
#     `name` varchar(50) NOT NULL,
#     `pwd` char(32) NOT NULL,
#     `insert_time` int(11) NOT NULL,
#     PRIMARY KEY (`id`)
#     ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
#     '''
#     res=dbObject.execute(sql)
#     print(res)

#写入数据
    # print("\n写入数据")
    # pwd = makeMd5("123456")
    # insert_time = getTime()
    # # timeArray=time.localtime(insert_time)
    # # print(time.strftime("%Y-%m-%d %H:%M:%S",timeArray))
    # res = dbObject.insert(table='user',name='dddd',pwd=pwd,insert_time=insert_time)
    # print("插入数据id为%s"%res)

#查询单条
    # print("\n查询数据-单条")
    # res = dbObject.fetchone(table='user', where="name='bbbb'")
    # print(res)

#查询多条
    # print("/n查询多条")
    # res =dbObject.fetchall(table='user',order='id desc',where="id>=3")
    # print(res,type(res))

#修改数据
    # print("\n修改数据")
    # res = dbObject.update(table="user",where="id=2",name="zzzz")
    # print("影响%s行"%res)

#删除数据
    # print("\n删除数据")
    # res = dbObject.delete(table="user", where="id=2")
    # print("影响%s行"%res)