import numpy as np
import myGlobal.myCls.msql as msql
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool

def Main(s):
    test1=s[0]
    test2=s[1]
    print(test1,test2)


if __name__=='__main__':
    pool = ThreadPool(10)
    list1 =[('1','2'),('3','4')]
    pool.map(Main,list1)
    pool.close
    pool.join

