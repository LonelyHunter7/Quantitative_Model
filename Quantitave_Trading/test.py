# encoding: UTF-8
import numpy as np
from pandas import Series
r=Series([5,10,20,25,30,25,21,23,45,62])
s=[30,40,50,60]
h=r.drop([len(r)-1])
print(h)

0   -0.215840
1    0.087310
2    0.169105
3   -0.120198
4    0.130334
5   -0.049459
Name: Close, dtype: float64
0   -0.055864
1   -0.024838
2   -0.029977
3    0.049289
4   -0.045947
Name: Close, dtype: float64
相关系数：-0.21477281551



0    0.087310
1    0.169105
2   -0.120198
3    0.130334
4   -0.049459
Name: Close, dtype: float64
0    0.058386
1   -0.012212
2   -0.013201
3    0.068411
4   -0.026687

#         lookback=250
#         holddays=25
#         self.ret_lag=((self.contract_Close-self.contract_Close.shift(lookback))/
#                       self.contract_Close.shift(lookback)).dropna()
#                       
#         self.ret_fut=((self.contract_Close-self.contract_Close.shift(holddays))/
#                       self.contract_Close.shift(holddays)).dropna()
#         
#         print(self.ret_lag)
#         print(self.ret_fut)
#         self.ret_fut=self.ret_fut[lookback+holddays:len(self.ret_lag)-1:lookback].reset_index(drop=True)
#         self.ret_lag=self.ret_lag[lookback:len(self.ret_lag)-1:lookback].reset_index(drop=True)
#         print(self.ret_lag)
#         print(self.ret_fut)
#         
#         
#           
#         if len(self.ret_lag)>len(self.ret_fut):
#             self.ret_lag=self.ret_lag.drop([len(self.ret_lag)-1])
#         elif len(self.ret_lag)<len(self.ret_fut):
#             self.ret_fut=self.ret_fut.drop([len(self.ret_fut)-1])
#          
#         #将seires的值取出来，进行后面的相关系数的计算
#         self.ret_lag=self.ret_lag.values
#         self.ret_fut=self.ret_fut.values
#          
#         #计算相关系数
#         if len(self.ret_lag)==len(self.ret_fut):
#             correlation=np.corrcoef(self.ret_lag,self.ret_fut)
#             print(u"相关系数："+str(correlation[0,1]))                     

class tuisong:
    def __init__(self):
        self.x=[1,2,3,4,5]
        self.y=[6,7,8,9,10]
        
    def rrr:
             
    def ontick(tick):
        print(tick)