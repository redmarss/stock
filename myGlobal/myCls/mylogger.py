#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import os


curPath = os.path.dirname(os.path.abspath(__file__))
rootPath = curPath[:curPath.find("myProject\\")+len("myProject\\")]     #获取根目录


class mylogger:
    def __init__(self, filepath='\stock\log\default.log', dlevel=logging.DEBUG,clevel=logging.DEBUG, flevel=logging.DEBUG):
        fullpath = rootPath+filepath
        if not os.path.exists(fullpath):        #文件不存在，则创建文件
            f = open(fullpath,'a+')
            f.close()

        print()
        self.logger = logging.getLogger(filepath)
        self.logger.setLevel(dlevel)
        fmt = logging.Formatter('[%(asctime)s]-[%(name)s]-[%(levelname)s]:[%(message)s]','%Y-%m-%d %H:%M:%S')
        #设置控制台日志
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(clevel)
        #设置文件日志
        fh = logging.FileHandler(fullpath)
        fh.setFormatter(fmt)
        fh.setLevel(flevel)

        self.logger.addHandler(sh)
        self.logger.addHandler(fh)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warnning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def cri(self, message):
        self.logger.critical(message)