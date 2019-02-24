import numpy as np
import myGlobal.myCls.msql as msql
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool




if __name__=='__main__':
    l =[i for i in range(100)]
    print(l)
    l_temp = l[:10]
