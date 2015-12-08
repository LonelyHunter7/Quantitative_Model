# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型描述：
    
"""
from gmsdk.api import StrategyBase
import time
import talib
import numpy as np
# from collections import deque
from gmsdk import *
    
#需要使用到的一些参数
LinearReglength=10  #线性回归通道的周期
roclength=2 #ROC的参数周期
N1=2.5  #移动止盈参数1
N2=2.5 #移动止盈参数2
N3=70 #保护性止损参数
LN1=1.5 #线性回归通道的里通道参数
LN2=2 #线性回归通道的外通道参数
atrlength=10  #ATR指标的参数 
eps = 1e-6 #控制变量
threshold = 0.235 #控制变量
    
    
class Redempion_moving1(StrategyBase):
    def __init__(self, *args, **kwargs):
        super(Redempion_moving1, self).__init__(*args, **kwargs)
        self.bar_type=60
        self.exchange="CZCE"
        self.sec_id="TA1601"
        self.last_price = 0.0
        self.symbol="CZCE.TA1601"
        self.window_size = 20
        self.trade_unit = [1.0, 2.0, 4.0, 8.0, 5.0, 3.0,2.0,1.0,1.0, 0.0] ##  [8.0, 4.0, 2.0, 1.0]
        self.trade_count = 0
        self.trade_limit = 1
        self.close=0
        self.high=0
#       self.timeperiod = self.config.getint('para', 'timeperiod') or 60
#         self.close_buffer = deque(maxlen=self.window_size)
#         self.significant_diff = self.config.getfloat('para', 'significant_diff') or significant_diff
            
        # prepare historical bars for MA calculating
        # 从数据服务中准备一段历史数据，使得收到第一个bar后就可以按需要计算ma
#         last_closes = [bar.close for bar in self.get_last_n_bars(self.symbol, self.bar_type, self.window_size)]
#         last_closes.reverse()     #因为查询出来的时间是倒序排列，需要倒一下顺序
#         self.close_buffer.extend(last_closes)
    
    
    # 响应bar数据到达事件
    def on_bar(self, bar):
        self.close=bar.close
        self.high=bar.high
        self.algo_action()
    # 响应tick数据到达事件
    def on_tick(self, tick):
        # 更新市场最新成交价
        self.last_price = tick.last_price    
        
    def on_execution(self, execution):
        #打印订单成交回报信息
        print("received execution: %s" % execution.exec_type)
         
    #策略的算法函数，策略的交易逻辑实现部分    
    def algo_action(self): 
        close=self.close
        high=self.high
# #         low=np.asarry(self.low_buffer)
#         #取10日的最近一日常规ATR值，并且取到小数点后一位
# #         ATR_=talib.ATR({"high":high,"low":low,"close":close,},timeperiods=atrlength)
# #         last_ATR=round(ATR,1)
#         #构建行情运行的区间通道，以10日指数平均线作为基准线，以atr作为通道的边沿距离参数
# #         ema=talib.MA(close,LinearReglength,matype=1)
#         last_ema=round(ema,1) #去最新值，且在小数点后一位
#         up_channel=last_ema+LN1*last_ATR #上通道
#         down_channel=last_ema-LN2*last_ATR #下通道
#         #各种所需要的过滤条件
# #         ma5=talib.MA(close,5,matype=0)
# #         ma10=talib.MA(close,10,matype=0)
# #         macd, macdsignal, macdhist = MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
#         #查询目前策略的仓位       
#         a_p = self.get_position(self.exchange, self.sec_id,OrderSide_Ask)    #查询策略所持有的空仓
#         b_p = self.get_position(self.exchange, self.sec_id,OrderSide_Bid)    #查询策略所持有的多仓   
#         #具体的开平仓条件
#         condition1=close-up_channel>threshold 
#         condition2=close-down_channel>threshold 
#         condition3=close-up_channel<-threshold 
#         condition4=close-down_channel<-threshold 
        #具体的交易逻辑
                # 如果本次下单量大于0,  发出买入委托交易指令
        self.open_long(bar.exchange, bar.sec_id, 0, 100)
        print("OpenLong: exchange %s, sec_id %s, price %s" % (bar.exchange, bar.sec_id, 0))
   
            
#             self.trade_count += 1    #增加计数
#             else:
#                 #  如果有空仓，且达到本次信号的交易次数上限
#                 if a_p:
#                     self.close_short(self.exchange, self.sec_id, self.last_price, a_p.volume)    # 平掉所有空仓
#                     self.trade_count = 0
                       
#         if  ma5>=ma10:
#             if (a_p is None) and self.trade_count < self.trade_limit:
#                   # 依次获取下单的交易量，下单量是配置的一个整数数列，用于仓位管理，可用配置文件中设置
#                 self.open_long(self.exchange, self.sec_id, self.last_price, 1)
#                 self.trade_count += 1    #增加计数
#             else:
#                 #  如果有空仓，且达到本次信号的交易次数上限
#                 if a_p  or self.trade_count == self.trade_limit:
#                     self.close_short(self.exchange, self.sec_id, self.last_price, a_p.volume)    # 平掉所有空仓
#                     self.trade_count = 0
#                     
#         if  self.close[-1]-self.high[-2]<0:
#  
#                 # 依次获取下单的交易量，下单量是配置的一个整数数列，用于仓位管理，可用配置文件中设
#                 # 如果本次下单量大于0,  发出买入委托交易指令
#             self.open_short(self.exchange, self.sec_id, self.last_price, 10)
#             self.trade_count += 1   #增加计数
#             else:
#             #  如果有空仓，且达到本次信号的交易次数上限
#                 if  b_p:
#                     self.close_short(self.exchange, self.sec_id, 0, a_p.volume)    # 平掉所有空仓
#                     self.trade_count = 0
                       
#         if condition4 and ma5<=ma10:
#             if (b_p is None) and self.trade_count < self.trade_limit:
#                   # 依次获取下单的交易量，下单量是配置的一个整数数列，用于仓位管理，可用配置文件中设置
#                     self.open_short(self.exchange, self.sec_id, self.last_price, vol)
#                     self.trade_count += 1    #增加计数
#             else:
#                 #  如果有空仓，且达到本次信号的交易次数上限
#                 if b_p or self.trade_count == self.trade_limit:
#                     self.close_short(self.exchange, self.sec_id, self.last_price, a_p.volume)    # 平掉所有空仓
#                     self.trade_count = 0
            
                        
if __name__ == '__main__':
    ret =Redempion_moving1(
    username='koluo713@163.com',
    password='wwii133',
    strategy_id='adb3391c-92a1-11e5-8cbe-1eac4c3dd87a',
    subscribe_symbols="CZCE.TA1601.bar.60",
    mode=4)
    ret.backtest_config(
    start_time='2013-11-1 9:00:00',
    end_time='2015-11-1 15:00:00',
    initial_cash=1000000,
    transaction_ratio=1,
    commission_ratio=0,
    slippage_ratio=0,
    price_type=1)
ret1=ret.run()
print('exit code: ', ret1)