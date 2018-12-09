#!/bin/usr/env python
# -*- coding:utf-8 -*-

class codeError(Exception):
    def __init__(self):
        self.args = ("股票代码错误",)
        self.message ='股票代码错误'
        self.code = 100

class dateError(ValueError):
    def __init__(self):
        self.args = ("输入日期不合法",)
        self.message = "输入日期不合法"
        self.code = 200

class notTradeDateError(Exception):
    def __init__(self):
        self.args = ("该日期非交易日",)
        self.message = "该日期非交易日"
        self.code = 300

class sqlError(Exception):
    def __init__(self):
        self.args = ("sql语句错误",)
        self.message = "sql语句错误"
        self.code = 400

class brokerError(Exception):
    def __init__(self):
        self.args = ("机构代码错误",)
        self.message = "机构代码错误"
        self.code = 500

class typeError(Exception):
    def __init__(self):
        self.args = ("输入参数类型错误",)
        self.message = "输入参数类型错误"
        self.code = 600

def RaiseError(error):
    try:
        raise error
    except error as e:
        print("错误代码:%s,原因:%s"%(e.code,e.message))


