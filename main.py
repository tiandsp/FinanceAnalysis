#-*- coding: UTF-8 -*-
from dataapiclient import Client
import matplotlib.pyplot as plt
from pylab import *
import json
import time
 
#得到當前系統日期
def getcurrenttime():
	return time.strftime("%Y%m%d",time.localtime(time.time()))


#得到n日平均曲線
def getavgprice(price,n):
	re= []
	for i in range(n):
		re.append(price[i])

	num=len(price)
	for i in range(n,num):
		tmp = 0.0
		for j in range(i-n,i):
			tmp = tmp + price[j]
		tmp = tmp / n
		re.append(tmp)	
	return re

#使用優礦數據接口
def getprice(url):
	code, result = client.getData(url)

	re=json.loads(result)

	num=len(re["data"])
	num_ser=range(num)

	preClosePrice=[]
	openPrice=[]
	highestPrice=[]
	lowestPrice=[]
	closePrice=[]
	accumAdjFactor=[]
	for i in num_ser: 
		preClosePrice.append(re["data"][i]["preClosePrice"])		#得到前一日收盤價
		openPrice.append(re["data"][i]["openPrice"])			#得到當天開盤價
		highestPrice.append(re["data"][i]["highestPrice"])		#得到當天最高價
		lowestPrice.append(re["data"][i]["lowestPrice"])		#得到當天最低價
		closePrice.append(re["data"][i]["closePrice"])			#得到當天收盤價
		accumAdjFactor.append(re["data"][i]["accumAdjFactor"])		#復權信息
	for i in num_ser:							#進行前復權
		preClosePrice[i]=preClosePrice[i]*accumAdjFactor[i]		
		openPrice[i]=openPrice[i]*accumAdjFactor[i]
		highestPrice[i]=highestPrice[i]*accumAdjFactor[i]
		lowestPrice[i]=lowestPrice[i]*accumAdjFactor[i]
		closePrice[i]=closePrice[i]*accumAdjFactor[i]
	return preClosePrice,openPrice,highestPrice,lowestPrice,closePrice

def getHLpriceN(Lprice,Hprice,n):
	highP=[]
	lowP=[]	
	for i in range(n):
		highP.append(Hprice[i])
		lowP.append(Lprice[i])			

	for i in range(n,len(Hprice)):
		tmpH=[]
		tmpL=[]
		for j in range(i-n,i):
			tmpH.append(Hprice[j])	
			tmpL.append(Lprice[j])	
		highP.append(max(tmpH))
		lowP.append(min(tmpL))
	return lowP,highP

#得到KDJ曲線
def getKDJ(C,LPrice,HPrice,n):		
	L,H=getHLpriceN(LPrice,HPrice,n)
	k=[]
	d=[]
	j=[]
	RSV=[]	
	for i in range(len(C)):
		if H[i]!=L[i]:
			rsv=(C[i]-L[i])/(H[i]-L[i])*100
		else:
			rsv=50
		RSV.append(rsv)	
		if i==0:			
			k.append(2/3.0*50+1/3.0*rsv)	
			d.append(2/3.0*50+1/3.0*k[i])	
		else:
			k.append(2/3.0*k[i-1]+1/3.0*rsv)
			d.append(2/3.0*d[i-1]+1/3.0*k[i])
		j.append(3*k[i]-2*d[i])

	return k,d,j

#得到SKD曲線
def getSKD(C,LPrice,HPrice,n):					
	k,d,j=getKDJ(C,LPrice,HPrice,n)	
	SK=d
	SD=getavgprice(SK,n)
	return SK,SD

#得到MACD曲線
def getMACD():
	
	return 1

def getbuy(price,avg_fast,avg_slow,th):
	buy=[]
	for i in range(len(price)):
		if i <= th:
			buy.append(0)
		else:
			if avg_fast[i-1]<avg_slow[i-1] and avg_fast[i]>avg_slow[i]:
				buy.append(price[i])
				#buy.append(avg_fast[i])			
			else:
				buy.append(0)
	return buy


def getsell(price,avg_fast,avg_slow,th):
	sell=[]
	for i in range(len(price)):
		if i <= th:
			sell.append(0)
		else:
			if avg_fast[i-1]>avg_slow[i-1] and avg_fast[i]<avg_slow[i]:
				sell.append(price[i])
				#sell.append(avg_fast[i])
			else:
				sell.append(0)
	return sell
	

#def getMaxp()

def getprofit(money,buy,sell):
	num=0
	profit=[];
	for i in range(len(buy)):
		if num==0:
			if buy[i]>0:
				num=money/buy[i]
		if num!=0:	
			if sell[i]>0:
				money = num*sell[i]
				num = 0;

		if num==0:
			pf=money
		if num!=0:	
			pf=num*price[i]

		profit.append(pf)
	return profit

#剔除原始數據中爲0的數據
def norPrice(p):
	re=[]
	tmp=0;
	for i in range(len(p)):
		if p[i] == 0:
			re.append(re[i-1])
		else:
			re.append(p[i])
	return re
	

fast=10
slow=30

money = 100000
starttime = '20090908'
endtime = getcurrenttime()
ticker='600595'
client = Client()
client.init('391009b17a789cc4885740ba934a341d4b01a16ccb4a177aa0b3d30d717cfbda')
url='/api/market/getMktEqud.json?field=&beginDate='+starttime+'&endDate='+endtime+'&ticker='+ticker
preClosePrice,openPrice,highestPrice,lowestPrice,closePrice=getprice(url)

price=norPrice(closePrice)

K,D,J=getKDJ(closePrice,lowestPrice,highestPrice,9)
SK,SD=getSKD(closePrice,lowestPrice,highestPrice,9)

avg_fast=getavgprice(price,fast)
avg_slow=getavgprice(price,slow)


buy=getbuy(price,avg_fast,avg_slow,slow)
sell=getsell(price,avg_fast,avg_slow,slow)

profit=getprofit(money,buy,sell)


print len(price)


figure(1)
plot(range(len(price)),price,'r');
plot(range(len(avg_fast)),avg_fast,'g')
plot(range(len(avg_slow)),avg_slow,'b')

plot(range(len(buy)),buy,'*')
plot(range(len(sell)),sell,'o')


figure(2)
plot(range(len(SK)),SK,'r')
plot(range(len(SD)),SD,'g')
#plot(range(len(J)),J,'b')

figure(3)
plt.plot(range(len(profit)),profit)


show()






