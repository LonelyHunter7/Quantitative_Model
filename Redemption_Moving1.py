# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型描述：

"""
from gmsdk.api import StrategyBase
import time
from talib.abstract import SMA
import numpy as np
from collections import deque
from gmsdk import *

#需要使用到的一些参数
LinearReglength=25  #线性回归通道的周期
fastlength=12 #MACD的快线参数
slowlength=26 #MACD的慢线参数
MACDlength=9 #MACD的参数周期
roclength=2 #ROC的参数周期
N1=2.5  #移动止盈参数1
N2=2.5 #移动止盈参数2
N3=70 #保护性止损参数
LN1=1.5 #线性回归通道的里通道参数
LN2=2 #线性回归通道的外通道参数
atrlength=10  #ATR指标的参数 



class Redempion_moving1(StrategyBase):
    def __init__(self, *args, **kwargs):
        super(MyStrategy, self).__init__(*args, **kwargs)
        self.last_price = 0.0
        self.window_size = self.config.getint('para', 'window_size') or 60
        self.timeperiod = self.config.getint('para', 'timeperiod') or 60
        self.bar_type = self.config.getint('para', 'bar_type') or 15
        self.close_buffer = deque(maxlen=self.window_size)
        self.significant_diff = self.config.getfloat('para', 'significant_diff') or significant_diff
        self.oc = True



    def on_bar(self, bar):
        if self.oc:
            self.open_long(bar.exchange, bar.sec_id, 0, 100)
        else:
            self.close_long(bar.exchange, bar.sec_id, 0, 100)
        self.oc = not self.oc
    
    def algo_action(self):
if currentbar>=1 then
begin
{entry signal} 
ATR=AvgTrueRange(atrlength);
minpoint=MinMove*PriceScale;
midline=LinearRegValue( C,LinearReglength, 0 );
upperband1=midline+LN1*ATR;
lowerband1=midline-LN1*ATR;
upperband2=midline+LN2*ATR; 
lowerband2=midline-LN2*ATR;
var2 = MACD( Close, fastlength, slowlength ) ; 
var3 = XAverage( var2, MACDLength ) ;
mvalue = var2 - var3 ; 
rvalue=Average(RSI(c,14),5); 
ma5=Average(c,5);
ma20=XAverage(c,20);

        
    


if __name__ == '__main__':
    mystrategy = MyStrategy(
        username='koluo713@163.com',
        password='wwii133',
        strategy_id='adb3391c-92a1-11e5-8cbe-1eac4c3dd87a',
        subscribe_symbols='SHSE.600000.bar.daily',
        mode=4,
        td_addr='localhost:8001')
    ret = mystrategy.backtest_config(
        start_time='2015-04-15 9:00:00',
        end_time='2015-05-15 15:00:00',
        initial_cash=1000000,
        transaction_ratio=1,
        commission_ratio=0,
        slippage_ratio=0,
        price_type=1)
    ret = mystrategy.run()
#    ret=mystrategy.stop()
    print('exit code: ', ret)
