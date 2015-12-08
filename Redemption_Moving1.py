# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型描述：
       
"""
from gmsdk.api import StrategyBase
import time
import talib
import numpy as np
from collections import deque
from pandas import Series,DataFrame
# import gmsdk

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
malength1=5
malength2=20 
eps = 1e-6
threshold = 0.235
tick_size = 0.2
half_tick_size = tick_size / 2
significant_diff = tick_size * 2.6      

              
class Redempion_moving1(StrategyBase):
    def __init__(self, *args, **kwargs):
        super(Redempion_moving1, self).__init__(*args, **kwargs)
        
        #各种所需要的配置信息
        self.symbol="CZCE.TA601"
        self.exchange="CZCE"
        self.sec_id="TA601"
        self.last_price = 0.0
        self.close=0.0
        self.high=0.0
        self.window_size = 10
        self.bar_type=60
        self.close_buffer = list()
        self.timeperiod=20
        self.trade_count=0.0
        self.open_buffer=list()
        #从数据服务中准备一段历史数据，使得收到第一个bar后就可以按需要计算ma
        data=self.get_last_n_bars(self.symbol, self.bar_type, self.window_size)
        close_list = [bar.close for bar in data]
        open_list=[bar.open for bar in data]
        self.close_buffer.extend(close_list)
        self.open_buffer.extend(open_list)

    def on_bar(self, bar):        
        if bar.bar_type==self.bar_type:
            self.close_buffer.append(bar.close)
            self.open_buffer.append(bar.open)
            self.algo_action()
               
    #响应tick数据到达事件
    def on_tick(self, tick):
        # 更新市场最新成交价
        self.last_price = tick.last_price    
#            
    def on_execution(self, execution):
         #打印订单成交回报信息
        print("received execution: %s" % execution.exec_type)
    
    def algo_action(self):
        #数据转换，方便后面的技术分析计算
        close=np.array(self.close_buffer)
        open=np.array(self.open_buffer)
        #主要的策略逻辑
        ma5=talib.MA(close,malength1,matype=0) 
        ma10=talib.MA(close,malength2,matype=0)
        delta=round(ma5[-1]-ma10[-1],4)
        miff=round(close[-1]-ma5[-1],4)
        flag=0
#         print(delta)
        #查询策略的仓位，用于仓位控制
        a_p = self.get_position(self.exchange, self.sec_id, 2)    #查询策略所持有的空仓
        b_p= self.get_position(self.exchange, self.sec_id, 1)    #查询策略所持有的多仓
                # 打印持仓信息
#         print ('pos long: {0} vwap: {1}, pos short: {2}, vwap: {3}'.format(b_p.volume if b_p else 0.0,
#                 round(b_p.vwap,2) if b_p else 0.0,
#                 a_p.volume if a_p else 0.0,
#                 round(a_p.vwap,2) if a_p else 0.0))
        
        #主要的交易逻辑
 
        close=np.array(self.close_buffer)
        open=np.array(self.open_buffer)
        if delta>0:
            if a_p is None:
                self.open_long(self.exchange, self.sec_id, self.last_price, 2) 
                print("OpenLong: exchange %s, sec_id %s, price %s" % (self.exchange, self.sec_id, self.last_price))

            elif a_P:
                self.close_short(self.exchange,self.sec_id,self.last_price,a_p.volume)
                print("Closeshort: exchange %s, sec_id %s, price %s" % (self.exchange, self.sec_id, self.last_price))
                
                           
        if delta<0:
            if b_p is None:
                self.open_short(self.exchange,self.sec_id,self.last_price,2)
                print("Openshort: exchange %s, sec_id %s, price %s" % (self.exchange, self.sec_id, self.last_price))
                
            elif b_p: 
                self.close_long(self.exchange, self.sec_id, self.last_price,2)
                print("Closelong: exchange %s, sec_id %s, price %s" % (self.exchange, self.sec_id, self.last_price))   

                
if __name__ == '__main__':
    ret =Redempion_moving1(
    username='koluo713@163.com',
    password='wwii133',
    strategy_id='adb3391c-92a1-11e5-8cbe-1eac4c3dd87a',
    subscribe_symbols="CZCE.TA601.bar.60",
    mode=2)
#     ret.backtest_config(
#     start_time='2014-3-28 9:00:00',
#     end_time='2015-10-28 15:00:00',
#     initial_cash=1000000,
#     transaction_ratio=1,
#     commission_ratio=0,
#     slippage_ratio=0,
#     price_type=1)
ret1=ret.run()
print('exit code: ', ret1)
