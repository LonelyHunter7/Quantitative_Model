# encoding: UTF-8

#研究部分需要用到的模块
import operator
import statsmodels.tsa.stattools as sts
import matplotlib.pyplot as plt
import pandas as pd
from dateutil.parser import parse
from scipy.stats.stats import pearsonr

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


class Pairs_Trading:
    """以豆粕和菜粕为例的配对交易，这只是一个测试实例
    目的是通过这个实例熟悉配对交易的主要流程，另外，这次是指定品种，
    而真正实际运用的时候可以还有筛选和比较的过程，这个过程今后要加进去.
    这一块是模型的研究部分，目的是为了检验品种的协整性，并得出相关参数"""
    def __init__(self):
        """Constructor"""
        
        #品种成员变量，用于储存读取结果
        self.contract1=None #品种1-豆粕
        self.contract2=None #品种2-菜粕
        
        #用于储存合约收盘价数据
        self.contract1_Close=None
        self.contract2_Close=None
        
        self.TradeData_Clean()
    def TradeData_Clean(self):
        """数据预处理"""
        #读取文件到变量中，用dataframe的格式储存
        self.contract1=pd.read_csv(r"E:\MAIZIPYTHON\Quantitave_Trading\m9000.csv",index_col="Date")
        self.contract2=pd.read_csv(r"E:\MAIZIPYTHON\Quantitave_Trading\RM000.csv",index_col="Date")
 
        #选取回测时期,这里是选取2013年全年的数据
        sector_contract1=self.contract1["2013/1/4":"2014/1/2"]
        sector_contract2=self.contract2["2013/1/4":"2014/1/2"]
  
        #把收盘价数据选取出来，并重新进行索引（用数字排序的方式，方便后面的计算处理）
        self.contract1_Close=sector_contract1["Close"].reset_index(drop=True)
        self.contract2_Close=sector_contract2["Close"].reset_index(drop=True)
        self.correlation_calculate()
        
 
    def  correlation_calculate(self):
        """相关系数的计算"""
        #计算品种日收益率,并去除缺失数据
        M_ret=((self.contract1_Close-self.contract1_Close.shift())/self.contract1_Close.shift()).dropna()
        RM_ret=((self.contract2_Close-self.contract2_Close.shift())/self.contract2_Close.shift()).dropna()
         
        #计算两个品种的共有回报项（日收益率时间序列）的相关系数
        rank={}
        if len(M_ret)==len(RM_ret): #两个序列必须长度相等
            correlation=np.corrcoef(M_ret.tolist(),RM_ret.tolist())
            rank["M_RM"]=correlation[0,1] #之所以采用这种写法是因为如果后期筛选的时候使用
        print(u"相关系数："+str(rank.items()))
        self.cointegration_test()
    def  cointegration_test(self):
        """协整检验，主要通过ADF检验的方式进行检验"""
        #协整检验，主要通过ADF检验的方式进行检验
        if len(self.contract1_Close) != 0 and len(self.contract2_Close) != 0:
            model=pd.ols(y=self.contract1_Close,x=self.contract2_Close,intercept=True)
            spread=self.contract1_Close-self.contract2_Close*model.beta["x"] #得出价差序列
            spread=spread.dropna() #去除缺失数据
            sta=sts.adfuller(spread,1) #进行ADF检验
            result=sta[0]
        print(sta)

class contract2(StrategyTemplate):
    def __init__(self):
        """Constructor"""
        super(contract2,self).__init__(name,symbol,engine)
       
        self.PairsTrading_Strategy=PairsTrading_Strategy()      
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
        
    def initStrategy(self,startData=None):
        """初始化策略"""
        self.initCompleted=True #回测用不到在往前读取历史数据这个过程。
                        
    #----------------------------------------------------------------------    
    def onTick(self,tick):
        """行情更新的相关处理，
                                这里的重点是用tick数据合成5分钟的bar数据，这里考虑到使用dataframe速度太慢，
                                还是用datetime格式时间作比较，进行行情数据的合成"""
                                
        self.currentTick=tick
        
        #因为直接是使用的日线数据回测，因此直接推送就可以了
        self.barOpen = tick.openPrice
        self.barHigh = tick.highPrice
        self.barLow = tick.lowPrice
        self.barClose = tick.lastPrice
        self.barVolume = tick.volume
        self.barTime = ticktime

        self.onBar(self.barOpen, self.barHigh, self.barLow, self.barClose, 
                   self.barVolume, self.barTime)
                   

                
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
        self.PairsTrading_Strategy.receive_contract2_data(self.listOpen,self.listHigh,self.listLow,self.listClose)
        
               
class PairsTrading_Strategy(StrategyTemplate):
    """模型的执行部分，包括接收数据并进行下单，以及更新仓位"""
    def __init__(self):
        """Constructor"""
        super(PairsTrading_Strategy,self).__init__(name,symbol,engine)
        
        self.model=pairs_trading() #将研究模型作为成员变量传入
        self.initalCash=100000 #初始资金
        self.AvailableCash=0 #当前可用资金
        self.dailyRetrun=0 #日收益率
        self.spread=None #价差的时间序列
        
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
        
        #品种X的K线数据储存
        self.contract2_listOpen=None
        self.contract2_listHigh=None
        self.contract2_listLow=None
        self.contract2_listClose=None

        
        #账户仓位
        self.pos=0
        
        #初始化是否完成
        self.initCompleted=False
        
        #读取历史数据的开始日期
        self.startdata=None
        
    #----------------------------------------------------------------------
    def receive_contract2_data(self,o,h,l,c):
        self.contract2_listOpen=o
        self.contract2_listHigh=h
        self.contract2_listLow=l
        self.contract2_listClose=c
        
        print(u"接收品种2的数据完成")
        
    #----------------------------------------------------------------------         
    def loadSetting(self,setting):
        """读取参数"""
        try:
           self.LinearReglength=setting["LinearReglength"]  #线性回归通道线参数
           self.smoothlength=setting["smoothlength"] #平滑参数

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
                                
        self.currentTick=tick
        
        #因为是用的日线数据做回测，因此直接推送数据就可以了，不用进行二次处理
        self.barOpen = tick.openPrice
        self.barHigh = tick.highPrice
        self.barLow = tick.lowPrice
        self.barClose = tick.lastPrice
        self.barVolume = tick.volume
        self.barTime = ticktime

        self.onBar(self.barOpen, self.barHigh, self.barLow, self.barClose, 
                   self.barVolume, self.barTime)

                
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
        
    def getDailyReturn(self)):
        """获取日收益率""" 
        
        
        
    
    def getAvailableCash(self):
        """计算当前资金"""
        
        
        
         
    def algo_action(self):
        """具体的策略"""
#         #首先进行一下格式转换，把list转换为talib需要的array数组格式
#         self.listClose=[float(x) for x in self.listClose] #因为array只能接受字符串格式，所以需要率先将所有整型数据进行格式转换
#         self.listOpen=[float(x) for x in self.listOpen]
#         self.listHigh=[float(x) for x in self.listHigh]
#         self.listLow=[float(x) for x in self.listLow]
#         
#         self.contract2_listClose=[float(x) for x in self.listClose] #因为array只能接受字符串格式，所以需要率先将所有整型数据进行格式转换
#         self.listOpen=[float(x) for x in self.listOpen]
#         self.listHigh=[float(x) for x in self.listHigh]
#         self.listLow=[float(x) for x in self.listLow]
        
         
        contract1_Close=self.listClose
        contract2_Close=self.contract2_listClose

        
        #进场信号
        """进场信号是利用到通道的穿越，包括通道里层线和通道外层线的穿越，
                                这个模型策略非常简单，后期可以以这个为蓝本，发展出更多的模型"""
                                
        #进场信号相关计算
        #获取研究部分得到的值
        beta = 0.418142479833;
        mean=7.27385228021;
        std  = 0.41596412236;
        
        #每次对冲的x品种头寸控制为当前持有现金的0.6
        contract1_Share = self.getAvailableCash()*0.6/contract1_Close[-1] #计算x品种的头寸 
        dailyReturn = self.getDailyReturn()
        initialCash = self.initalCash
        contract2_Share = beta*contract1_Share #计算y品种头寸
        
        if contract1_Share > 100:
            contract1_Share =100 #最大头寸数目不得超过100
            
        #计算两只股票之间的价差
        self.spread = contract2_Close[-1] - beta*contract1_Close[-1]
        #计算zScore
        zScore = (self.spread - mean)/std;
        plt.plot("zScore", zScore)
        plt.show()
        
    #当入场信号来的时候，进入市场  
    if zScore > 1.1 and self.pos1 == 0 and self.pos2 == 0:               
        self.short(self.currentTick2.lastPrice, contract2_Share ,self.currentTick2.time)
        self.buy(self.currentTick1.lastPrice,contract1_Share,self.currentTick1.time)
                
    if zScore < -1.5 and self.pos1 == 0 and self.pos2 == 0:               
        self.buy(self.currentTick2.lastPrice, contract2_Share ,self.currentTick2.time)
        self.short(self.currentTick1.lastPrice,contract1_Share,self.currentTick1.time)
        
    #当出场信号来的时候，离开市场
    if zScore < 0.8 and zScore > -1.0 and self.pos1 != 0  and  self.pos2 != 0:
        if self.pos1 > 0 :
            self.sell(self.currentTick1.lastPrice, contract1_Share ,self.currentTick1.time)
            
        if self.pos1 < 0:
            self.cover(self.currentTick1.lastPrice, contract1_Share ,self.currentTick1.time)    
        
        if self.pos2 > 0:
            self.sell(self.currentTick2.lastPrice, contract2_Share ,self.currentTick2.time)
        
        if self.pos2 < 0:
            self.cover(self.currentTick2.lastPrice, contract2_Share ,self.currentTick2.time))
            
    #止损，如果亏损超过4天的时间，那么进行清仓        
    if dailyReturn < 0:
        count = count + 1

    #----------------------------------------------------------------------       
#     def strToTime(self, t, ms):
#         """从字符串时间转化为time格式的时间"""
#         hh, mm, ss = t.split(':')
#         tt = time(int(hh), int(mm), int(ss), microsecond=ms)
#         return tt

########################################################################
def print_Log(event):
    log=event.dict_["log"]
    print(str(datetime.now())+u","+log)

if __name__=="__main__":
    Pairs_Trading()





