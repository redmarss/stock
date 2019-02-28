import numpy as np
import myGlobal.myCls.msql as msql
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool




https://gupiao.baidu.com/api/stocks/stockdaybar?from=pc&os_ver=1&cuid=xxx&vv=100&format=json&stock_code=sh600500&step=3&start=20170105&count=160&fq_type=no


start：日期参数，不填则为今天
count:获取数量
fq_type：front/back/no