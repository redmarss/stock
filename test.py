import numpy as np
import myGlobal.myCls.msql as msql
import pandas as pd

dbObject =msql.SingletonModel(host='localhost', port='3306', user='root', passwd='redmarss',
                              db='tushare', charset='utf8')


t = dbObject.fetchall(table="stock_trade_history_info",field="stock_code,ts_date")
df = pd.DataFrame(list(t),columns=["stock_code","ts_date"])

dbObject.DataframeToSql(df,"qualification")