#### Broker

​	_getBuyStock()

​	@property	brokercode

​	@property	ts_date

#### Stock

​	_getbuyBroker()

​	_next_some_days(*startdate=None ,days=7*)

​	@property   stockname

​	@property   ts_date

​	@property   stockcode

​	@property   open_price

​	@property   close_price

​	@property   high_price

​	@property   low_price

​	@property   volume

#### Simulate.BrokerSimulate(*brokercode,ts_date,ftype=1,amount=1000,tablename="simulate_buy"*)

​	_createtable(*tablename*)

​	**simulateBuy()**

​	__is_simulate(*stockcode,ftype*)		#判断brokercode,ts_date,stockcode,ftype是否模拟过

​	__update_ftype							#更新ftype数值

​	__recordToSql								#将模拟结果存入数据库



#### Strategy(Stock)

strategy()				#根据self.ftype来模拟计算

_cacuscore()		#计算此次模拟的机构得分





​	

​	

