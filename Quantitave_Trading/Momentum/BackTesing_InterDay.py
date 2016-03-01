# encoding: UTF-8

#首先添加需要的地址方便进行模块引用
import sys
sys.path.append(r"E:\MAIZIPYTHON\Quantitave_Trading\Momentum")
sys.path.append(r"E:\MAIZIPYTHON\Quantitave_Strategy_Model\vn.strategy\strategydemo")

from strategyEngine import *
from backtestingEngine import *
from Back_InterDay_Momentum_Time_Series import InterDay_Momentum_Strategy



# 回测脚本    
if __name__ == '__main__':
    symbol = 'TA605'
    
    # 创建回测引擎
    be = BacktestingEngine()
    
    # 创建策略引擎对象
    se = StrategyEngine(be.eventEngine, be, backtesting=True)
    be.setStrategyEngine(se)
    
    # 初始化回测引擎
    be.connectMongo()
    be.loadDataHistory(symbol, "2015/1/5", "2015/12/28")
    
    #创建策略
    setting={}
    setting["backdays"]=60  
    setting["holddays"]=25 
    
#     setting['startDate'] = datetime(year=2015, month=5, day=20)
    se.createStrategy(u"隔夜动力策略","TA605",InterDay_Momentum_Strategy,setting)
    
    # 启动所有策略
    se.startAll()
    
    # 开始回测
    be.startBacktesting()
