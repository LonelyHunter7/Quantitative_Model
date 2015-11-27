from CAL.PyCAL import *
import numpy as np
from pandas import DataFrame

start = '2011-08-01'                       # 回测起始时间
end = '2015-08-01'                         # 回测结束时间
benchmark = 'HS300'                        # 策略参考标准
universe = set_universe('HS300')  # 证券池，支持股票和基金
capital_base = 10000000                      # 起始资金
freq = 'd'                                 # 策略类型，'d'表示日间策略使用日线回测，'m'表示日内策略使用分钟线回测
refresh_rate = 1                           # 调仓频率，表示执行handle_data的时间间隔，若freq = 'd'时间间隔的单位为交易日，若freq = 'm'时间间隔为分钟

# 构建日期列表
data=DataAPI.TradeCalGet(exchangeCD=u"XSHG",beginDate=u"20110801",endDate=u"20150801",field=['calendarDate','isMonthEnd'],pandas="1")
data = data[data['isMonthEnd'] == 1]
date_list = data['calendarDate'].values.tolist()

cal = Calendar('China.SSE')
period = Period('-1B')

def initialize(account):                   # 初始化虚拟账户状态
    pass

def handle_data(account):                  # 每个交易日的买入卖出指令
    
    today = account.current_date
    today = Date.fromDateTime(account.current_date)  # 向前移动一个工作日
    yesterday = cal.advanceDate(today, period)
    yesterday = today.toDateTime()
    
    if yesterday.strftime('%Y-%m-%d') in date_list:
        
        # 净利润增长率
        NetProfitGrowRate =DataAPI.MktStockFactorsOneDayGet(tradeDate=yesterday.strftime('%Y%m%d'),secID=account.universe,field=u"secID,NetProfitGrowRate",pandas="1")
        NetProfitGrowRate.columns = ['secID','NetProfitGrowRate']
        NetProfitGrowRate['ticker'] = NetProfitGrowRate['secID'].apply(lambda x: x[0:6])
        NetProfitGrowRate.set_index('ticker',inplace=True)
        ep = NetProfitGrowRate['NetProfitGrowRate'].dropna().to_dict()
        signal_NetProfitGrowRate = standardize(neutralize(winsorize(ep),yesterday.strftime('%Y%m%d')))  # 对因子进行去极值、中性化、标准化处理得信号
        
        # 权益收益率
        ROE = DataAPI.MktStockFactorsOneDayGet(tradeDate=yesterday.strftime('%Y%m%d'),secID=account.universe,field=u"secID,ROE",pandas="1")
        ROE.columns = ['secID','ROE']
        ROE['ticker'] = ROE['secID'].apply(lambda x: x[0:6])
        ROE.set_index('ticker',inplace=True)
        ep = ROE['ROE'].dropna().to_dict()
        signal_ROE = standardize(neutralize(winsorize(ep),yesterday.strftime('%Y%m%d')))  # 对因子进行去极值、中性化、标准化处理得信号
        
        # RSI
        RSI = DataAPI.MktStockFactorsOneDayGet(tradeDate=yesterday.strftime('%Y%m%d'),secID=account.universe,field=u"secID,RSI",pandas="1")
        RSI.columns = ['secID','RSI']
        RSI['ticker'] = RSI['secID'].apply(lambda x: x[0:6])
        RSI.set_index('ticker',inplace=True)
        ep = RSI['RSI'].dropna().to_dict()
        if len(ep) == 0 :
            return
        signal_RSI = standardize(neutralize(winsorize(ep),yesterday.strftime('%Y%m%d'))) # 对因子进行去极值、中性化、标准化处理得信号
        
        # 构建组合score矩阵
        weight = np.array([0.4, 0.3, 0.3])   #　信号合成，各因子权重
        Total_Score = DataFrame(index=RSI.index, columns=['NetProfitGrowRate','ROE','RSI'], data=0)
        Total_Score['NetProfitGrowRate'][signal_NetProfitGrowRate.keys()] = signal_NetProfitGrowRate.values()
        Total_Score['ROE'][signal_ROE.keys()] = signal_ROE.values()
        Total_Score['RSI'][signal_RSI.keys()] = signal_RSI.values()
        Total_Score['total_score'] = np.dot(Total_Score, weight)
        
        total_score = Total_Score['total_score'].to_dict()
        wts = simple_long_only(total_score, today.strftime('%Y%m%d'))   # 调用组合构建函数，组合构建综合考虑各因子大小，行业配置等因素，默认返回前30%的股票
        
        # 找载体，将ticker转化为secID
        RSI['wts'] = np.nan
        RSI['wts'][wts.keys()] = wts.values()
        RSI = RSI[~np.isnan(RSI['wts'])]
        RSI.set_index('secID', inplace=True)
        RSI.drop('RSI', axis=1, inplace=True)

        # 先卖出
        sell_list = account.valid_secpos
        for stk in sell_list:
            order_to(stk, 0)

        # 再买入
        buy_list = RSI.index
        total_money = account.referencePortfolioValue
        prices = account.referencePrice 
        for stk in buy_list:
            if np.isnan(prices[stk]) or prices[stk] == 0:  # 停牌或是还没有上市等原因不能交易
                continue
            order(stk, int(total_money * RSI.loc[stk]['wts'] / prices[stk] /100)*100)
    else:
        return
