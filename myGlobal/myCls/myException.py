#!/bin/usr/env python
# -*- coding -*-
import datetime
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

    def RaisedateError(self):
        try:
            raise self
        except self as e:
            print(self.message)

class notTradeDateError(Exception):
    def __init__(self):
        self.args = ("该日期非交易日",)
        self.message = "该日期非交易日"
        self.code = 300

def RaiseError(error):
    try:
        raise error
    except error as e:
        print("错误代码:%s,原因:%s"%(e.code,e.message))

