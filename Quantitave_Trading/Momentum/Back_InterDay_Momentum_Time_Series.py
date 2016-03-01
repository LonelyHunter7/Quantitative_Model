# encoding: UTF-8

"""模型概述：隔夜动量策略，且为time series strategies，
也就是根据过去两段不同时期(lag)内期货合约的回报率的相关性作为基础进行架构，
这两个时期长度也是整个策略的核心参数。
该模型的理论基础是:对于期货合约来说,roll return 的方向不经常改变，或者说改变的速度很缓慢。
整个策略分为研究部分和执行部分两个部分。"""


#研究部分需要用到的模块
import operator
import statsmodels.tsa.stattools as sts
# import matplotlib.pyplot as plt
import pandas as pd
from dateutil.parser import parse
from scipy.stats.stats import pearsonr
import scipy.stats as SS

#执行部分需要用到的模块
import sys
sys.path.append(r"E:\MAIZIPYTHON\Quantitave_Strategy_Model\vn.strategy\strategydemo")
from datetime import datetime,timedelta,time
from time import sleep 

#引入第三方模块
import sip
from PyQt4 import QtCore
import talib
import numpy as np
from pandas import Series,DataFrame

#引入自己写的模块
from demoEngine import MainEngine
from strategyEngine import *

########################################################################

"""策略的研究部分，主要用于计算相关系数、P-value值"""
class Time_Series_Momentum:
    """以豆粕和菜粕为例的配对交易，这只是一个测试实例
    目的是通过这个实例熟悉配对交易的主要流程，另外，这次是指定品种，
    而真正实际运用的时候可以还有筛选和比较的过程，这个过程今后要加进去.
    这一块是模型的研究部分，目的是为了检验品种的协整性，并得出相关参数"""
    def __init__(self):
        """Constructor"""
        """以豆粕期货作为例子"""
        
        #回测期和持有期的收益率，用numpy数组的格式进行储存
        self.ret_lag=None #回测期的收益率
        self.ret_fut=None #持有期的收益率
        
        #用于储存合约收盘价数据
        self.contract=None
        self.contract_Close=None 
                
        #储存相关系数结果的字典
        self.rank={}
        self.TradeData_Clean()

    #----------------------------------------------------------------------           
    def TradeData_Clean(self):
        """数据预处理"""
        #读取文件到变量中，用dataframe的格式储存
        self.contract=pd.read_csv(r"E:\TA000.csv",index_col=["Date"])

        #选取回测时期,这里是选取2013年全年的数据
        sector_contract=self.contract["2012/1/4":"2014/12/31"]  

  
        #把收盘价数据选取出来，并重新进行索引(索引用数字排序的方式，方便后面的计算处理)
        self.contract_Close=sector_contract["Close"].reset_index(drop=True)
        
        self.correlation_calculate()
        
    #----------------------------------------------------------------------       
    def  correlation_calculate(self):
        """相关系数的计算"""
        #计算过去和未来两个时期的收益率
        for lookback in [10,25,60,120,250]:
            for holddays in [1,5,10,25,60,120,250]:
                if lookback >holddays:        
                    self.ret_lag=((self.contract_Close-self.contract_Close.shift(lookback))/
                                  self.contract_Close.shift(lookback)).dropna()
                         
                      
                    self.ret_fut=((self.contract_Close-self.contract_Close.shift(holddays))/
                                  self.contract_Close.shift(holddays)).dropna()
                                   
                    self.ret_fut=self.ret_fut[lookback+holddays:len(self.ret_lag):lookback].reset_index(drop=True)
                    self.ret_lag=self.ret_lag[lookback:len(self.ret_lag):lookback].reset_index(drop=True)
                     
                      
                    if len(self.ret_lag)>len(self.ret_fut):
                        self.ret_lag=self.ret_lag.drop([len(self.ret_lag)-1])
                    elif len(self.ret_lag)<len(self.ret_fut):
                        self.ret_fut=self.ret_fut.drop([len(self.ret_fut)-1])
                      
                    #将seires的值取出来，进行后面的相关系数的计算
                    self.ret_lag=self.ret_lag.values
                    self.ret_fut=self.ret_fut.values
  
                    #计算相关系数
                    if len(self.ret_lag)==len(self.ret_fut):
                        correlation=np.corrcoef(self.ret_lag,self.ret_fut)
                        P_value=SS.ttest_rel(self.ret_lag, self.ret_fut,axis=0)
#                         print(str(lookback)+u","+str(holddays)+u"相关系数:"+str(correlation[0,1]))
                    m="lookback"+":"+str(lookback)+","+"holddays"+":"+str(holddays)
                    self.rank[m]=correlation[0,1]
        rank1 = sorted(self.rank.items(), key=operator.itemgetter(1))                 
        print(rank1[-5:]) #这里最好是经过人工判断，并且每隔一段时间要重新计算一次。
        print(P_value)
        
        
########################################################################
"""策略的执行部分"""
class InterDay_Momentum_Strategy(StrategyTemplate):
    """模型的执行部分，包括接收数据并进行下单，以及更新仓位"""
    def __init__(self,name, symbol, engine):
        """Constructor"""
        super(InterDay_Momentum_Strategy,self).__init__(name,symbol,engine)
         
        #模型参数
        self.backdays=0 #回测日参数
        self.holddays=0 #持有日参数
        self.ATRlength=0 #ATR的时间参数
        
        #控制进出场的参数
        self.flagb=False
        self.flags=False
        self.countGet=0 #用于计数，目的是控制进出场 
         
        #K线数据的表示    
        self.barOpen=0
        self.barHigh=0
        self.barLow=0
        self.barClose=0
        self.Volume=0
        self.barTime=None
         
        #保存K线数据的李彪
        self.listOpen=[]
        self.listHigh=[]
        self.listLow=[]
        self.listClose=[]
        self.listVolume=[]
        self.listTime=[]
                 
        #账户仓位
        self.pos=0
         
        #初始化是否完成
        self.initCompleted=False
         
        #读取历史数据的开始日期
        self.startdata=None
         
    #----------------------------------------------------------------------         
    def loadSetting(self,setting):
        """读取参数"""
        try:
            #采用从外部读取参数的方式
           self.backdays=setting["backdays"]  
           self.holddays=setting["holddays"]  
           
           print(self.name+u"读取参数成功")
        except KeyError:
            print(self.name+u"读取参数错误，检查读取参数设置")
             
        try:
            self.initStrategy(setting["startData"])
        except KeyError:
            self.initStrategy()    
             
    #----------------------------------------------------------------------
    def initStrategy(self,startData=None):
        """初始化策略"""
        self.initCompleted=True #回测用不到在往前读取历史数据这个过程。
                         
    #----------------------------------------------------------------------    
    def onTick(self,tick):
        """行情更新的相关处理，
                                这里的重点是用tick数据合成5分钟的bar数据，这里考虑到使用dataframe速度太慢，
                                还是用datetime格式时间作比较，进行行情数据的合成"""
                                
        td=timedelta(minutes=15) #取五分钟的时间间隔 
        self.currentTick=tick
        ticktime=datetime.strptime(tick.time,"%Y/%m/%d %H:%M:%S")

        #检查是否是接收第一笔tick
        if self.barOpen == 0:
            # 初始化新的K线数据
            self.barOpen = tick.openPrice
            self.barHigh = tick.highPrice
            self.barLow = tick.lowPrice
            self.barClose = tick.lastPrice
            self.barVolume = tick.volume
            self.barTime = ticktime
        else:
             # 如果是当前一分钟内的数据
            if ticktime-self.barTime <=td:
                 # 汇总TICK生成K线   
                self.barHigh = max(self.barHigh, tick.lastPrice)
                self.barLow = min(self.barLow, tick.lastPrice)
                self.barClose = tick.lastPrice
                self.barVolume = self.barVolume + tick.volume
                self.barTime = ticktime                
            # 如果是新一分钟的数据
            else:
                # 首先推送K线数据
                self.onBar(self.barOpen, self.barHigh, self.barLow, self.barClose, 
                           self.barVolume, self.barTime)
                   
                # 初始化新的K线数据
                self.barOpen = tick.openPrice
                self.barHigh = tick.highPrice
                self.barLow = tick.lowPrice
                self.barClose = tick.lastPrice
                self.barVolume = tick.volume
                self.barTime = ticktime     

                 
    #----------------------------------------------------------------------        
    def onTrade(self,trade):
        """更新账户仓位"""
        if trade.direction==DIRECTION_BUY:
            self.pos +=trade.volume
        else:
            self.pos -=trade.volume
         
        log=self.name+u'当前仓位：'+str(self.pos)
        print(u"更新仓位完成")
         
    #----------------------------------------------------------------------          
    def onOrder(self,orderRef):
        """报单更新""" 
         
        pass
  
    #----------------------------------------------------------------------     
    def onStopOrder(self,so):
        """停止单更新"""
         
        pass
     
    #----------------------------------------------------------------------   
    def onBar(self,o,h,l,c,volume,time):
        """K线数据更新的处理，策略中最核心的一步，前面所有的步骤都是为了这一步做准备"""
        #保存K线数据到K线列表中
        self.listOpen.append(o)
        self.listHigh.append(h)
        self.listLow.append(l)
        self.listClose.append(c)
        self.listVolume.append(volume)
        self.listTime.append(time) 
        self.algo_action()
         
    def getDailyReturn(self):
        """获取日收益率""" 
        pass
     
    #----------------------------------------------------------------------               
    def getAvailableCash(self):
        """计算当前资金"""
 
        pass
     
    #----------------------------------------------------------------------                  
    def algo_action(self):
        """具体的策略"""
        #首先进行一下格式转换，把list转换为talib需要的array数组格式
        self.listClose=[float(x) for x in self.listClose] #因为array只能接受字符串格式，所以需要率先将所有整型数据进行格式转换
        self.listOpen=[float(x) for x in self.listOpen]
        self.listHigh=[float(x) for x in self.listHigh]
        self.listLow=[float(x) for x in self.listLow]

        open=np.array(self.listOpen)
        high=np.array(self.listHigh)
        low=np.array(self.listLow)
        close=np.array(self.listClose)

        #进场信号
        """进场信号是利用到通道的穿越，包括通道里层线和通道外层线的穿越，
                                这个模型策略非常简单，后期可以以这个为蓝本，发展出更多的模型"""
                                 
        #进场信号相关计算
        self.ATR=talib.ATR(high, low, close, timeperiod=14)   #计算ATR 
        if len(close) >60:
        #当入场信号来的时候，进入市场  
            if (close[-1] > close[-60] +4*self.ATR[-1]) and self.flagb==False and self.flags==False:
                self.buy(self.currentTick.lastPrice,1,self.currentTick.time)
                self.flagb=True
 
                 
            if  (close[-1]< close[-60] -4 *self.ATR[-1])  and self.flags==False and  self.flagb==False:               
                self.short(self.currentTick.lastPrice,1,self.currentTick.time)
                self.flags=True
            

            #出场信号 ，当
            if self.flagb==True :
                self.countGet +=1
                if self.countGet >25:
                    self.sell(self.currentTick.lastPrice, 1 ,self.currentTick.time)
                    self.countGet=0
                    self.flagb=False
            
            if self.flags==True :
                self.countGet +=1
                if self.countGet >25:
                    self.cover(self.currentTick.lastPrice, 1 ,self.currentTick.time) 
                    self.countGet=0
                    self.flags=False
             
########################################################################
def print_Log(event):
    log=event.dict_["log"]
    print(str(datetime.now())+u","+log)

########################################################################      
if __name__=="__main__":
    Time_Series_Momentum()
    