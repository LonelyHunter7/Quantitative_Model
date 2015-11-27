from CAL.PyCAL import *
import numpy as np
from pandas import DataFrame

start = '2011-08-01'                       # �ز���ʼʱ��
end = '2015-08-01'                         # �ز����ʱ��
benchmark = 'HS300'                        # ���Բο���׼
universe = set_universe('HS300')  # ֤ȯ�أ�֧�ֹ�Ʊ�ͻ���
capital_base = 10000000                      # ��ʼ�ʽ�
freq = 'd'                                 # �������ͣ�'d'��ʾ�ռ����ʹ�����߻ز⣬'m'��ʾ���ڲ���ʹ�÷����߻ز�
refresh_rate = 1                           # ����Ƶ�ʣ���ʾִ��handle_data��ʱ��������freq = 'd'ʱ�����ĵ�λΪ�����գ���freq = 'm'ʱ����Ϊ����

# ���������б�
data=DataAPI.TradeCalGet(exchangeCD=u"XSHG",beginDate=u"20110801",endDate=u"20150801",field=['calendarDate','isMonthEnd'],pandas="1")
data = data[data['isMonthEnd'] == 1]
date_list = data['calendarDate'].values.tolist()

cal = Calendar('China.SSE')
period = Period('-1B')

def initialize(account):                   # ��ʼ�������˻�״̬
    pass

def handle_data(account):                  # ÿ�������յ���������ָ��
    
    today = account.current_date
    today = Date.fromDateTime(account.current_date)  # ��ǰ�ƶ�һ��������
    yesterday = cal.advanceDate(today, period)
    yesterday = today.toDateTime()
    
    if yesterday.strftime('%Y-%m-%d') in date_list:
        
        # ������������
        NetProfitGrowRate =DataAPI.MktStockFactorsOneDayGet(tradeDate=yesterday.strftime('%Y%m%d'),secID=account.universe,field=u"secID,NetProfitGrowRate",pandas="1")
        NetProfitGrowRate.columns = ['secID','NetProfitGrowRate']
        NetProfitGrowRate['ticker'] = NetProfitGrowRate['secID'].apply(lambda x: x[0:6])
        NetProfitGrowRate.set_index('ticker',inplace=True)
        ep = NetProfitGrowRate['NetProfitGrowRate'].dropna().to_dict()
        signal_NetProfitGrowRate = standardize(neutralize(winsorize(ep),yesterday.strftime('%Y%m%d')))  # �����ӽ���ȥ��ֵ�����Ի�����׼��������ź�
        
        # Ȩ��������
        ROE = DataAPI.MktStockFactorsOneDayGet(tradeDate=yesterday.strftime('%Y%m%d'),secID=account.universe,field=u"secID,ROE",pandas="1")
        ROE.columns = ['secID','ROE']
        ROE['ticker'] = ROE['secID'].apply(lambda x: x[0:6])
        ROE.set_index('ticker',inplace=True)
        ep = ROE['ROE'].dropna().to_dict()
        signal_ROE = standardize(neutralize(winsorize(ep),yesterday.strftime('%Y%m%d')))  # �����ӽ���ȥ��ֵ�����Ի�����׼��������ź�
        
        # RSI
        RSI = DataAPI.MktStockFactorsOneDayGet(tradeDate=yesterday.strftime('%Y%m%d'),secID=account.universe,field=u"secID,RSI",pandas="1")
        RSI.columns = ['secID','RSI']
        RSI['ticker'] = RSI['secID'].apply(lambda x: x[0:6])
        RSI.set_index('ticker',inplace=True)
        ep = RSI['RSI'].dropna().to_dict()
        if len(ep) == 0 :
            return
        signal_RSI = standardize(neutralize(winsorize(ep),yesterday.strftime('%Y%m%d'))) # �����ӽ���ȥ��ֵ�����Ի�����׼��������ź�
        
        # �������score����
        weight = np.array([0.4, 0.3, 0.3])   #���źźϳɣ�������Ȩ��
        Total_Score = DataFrame(index=RSI.index, columns=['NetProfitGrowRate','ROE','RSI'], data=0)
        Total_Score['NetProfitGrowRate'][signal_NetProfitGrowRate.keys()] = signal_NetProfitGrowRate.values()
        Total_Score['ROE'][signal_ROE.keys()] = signal_ROE.values()
        Total_Score['RSI'][signal_RSI.keys()] = signal_RSI.values()
        Total_Score['total_score'] = np.dot(Total_Score, weight)
        
        total_score = Total_Score['total_score'].to_dict()
        wts = simple_long_only(total_score, today.strftime('%Y%m%d'))   # ������Ϲ�����������Ϲ����ۺϿ��Ǹ����Ӵ�С����ҵ���õ����أ�Ĭ�Ϸ���ǰ30%�Ĺ�Ʊ
        
        # �����壬��tickerת��ΪsecID
        RSI['wts'] = np.nan
        RSI['wts'][wts.keys()] = wts.values()
        RSI = RSI[~np.isnan(RSI['wts'])]
        RSI.set_index('secID', inplace=True)
        RSI.drop('RSI', axis=1, inplace=True)

        # ������
        sell_list = account.valid_secpos
        for stk in sell_list:
            order_to(stk, 0)

        # ������
        buy_list = RSI.index
        total_money = account.referencePortfolioValue
        prices = account.referencePrice 
        for stk in buy_list:
            if np.isnan(prices[stk]) or prices[stk] == 0:  # ͣ�ƻ��ǻ�û�����е�ԭ���ܽ���
                continue
            order(stk, int(total_money * RSI.loc[stk]['wts'] / prices[stk] /100)*100)
    else:
        return
