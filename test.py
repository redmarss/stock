import pandas_datareader.data as web
import datetime

df_stockload=web.DataReader("600797.SS","yahoo",datetime.datetime(2018,1,1),datetime.datetime.today())
print(df_stockload)