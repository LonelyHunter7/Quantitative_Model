# encoding: UTF-8

#引入系统模块
import csv

#引入第三方模块
import pandas as pd
from pandas import Series,DataFrame
from numpy import cumsum 
import matplotlib.pyplot as plt
from datetime import datetime,time 
 


class TradeData_Analysis():
    """成交记录的数据处理包含三个部分：
    1.数据的预处理,将数据存放在dataframe中
    2.利用dataframe格式的便利，对成交记录进行数理统计分析
    3.将统计分析的结果进行存放"""
    def __init__(self):
        """Constructor"""
        
        #用于存放成交记录的DataFrame容器
        self.frame=None
        
        #绩效分析
        self.profit={} #交易盈利单的字典
        self.loss={} #交易亏损单的字典
        self.total_profit=0 #交易总盈利
        self.total_loss=0 #交易总亏损
        self.retained_porfit=0 #交易净利润
        
        self.total_tradenumber=0 #总交易次数
        self.success_rate=0 #交易成功率
        
        self.continuous_profit_number=0 #最大连续亏损次数
        self.continuous_loss_number=0 #最大连续盈利次数
        
        self.cumsum_profit=0 #各个时间带你的权益
        self.max_retracement=0 #交易最大回撤
        
        self.time_trade={} #计算每个时间点对应的收益和亏损值，用于后面的绘图
        
        self.fig=None #当前的画图fig对象
        self.record={} #用于储存绩效的字典
        

    def TradeData_Clean(self,filename):
        """1.成交记录的数据预处理"""
        with open(filename) as f:
            reader=csv.reader(f)
            results=[]
            data_dict={}
            save_index=[]
            for line in reader:
                lines=eval(line[0])
                InstrumentID=lines["InstrumentID"]
                Direction=lines["Direction"] 
                OffsetFlag=lines["OffsetFlag"]
                TradeID=lines["TradeID"]
                Price=lines["Price"] 
                OrderRef=lines["OrderRef"]
                Volume=lines['Volume']
                Time=lines["Time"]
                results=[InstrumentID,Direction,OffsetFlag,TradeID,Price,OrderRef,Volume,Time]
                data_dict[OrderRef]=results    
            self.frame=DataFrame(data_dict).T
            states=["InstrumentID","Direction","OffsetFlag","TradeID","Price","OrderRef",'Volume',"Time"]
            self.frame.columns=states
            indexs=self.frame.index
            for data in indexs:
                data=int(data)
                save_index.append(data)
            self.frame.index=save_index
            self.frame=self.frame.sort_index()
#             print(self.frame)
            
            
    def mathematical_statistics(self):
        """2.成交记录的数理统计"""
        index=0
        resolution=0
        profit_values=[]
        loss_values=[]
        trade=[]
        profit_number=0
        loss_number=0
        profit_numbers=[]
        loss_numbers=[]
        all=[]
        #首先取完整交易的数字，也就是保证计算的交易是偶数次
        if len(self.frame.index) %2==0:
            resolution=len(self.frame.index)
        elif len(self.frame.index)%2 !=0:
            resolution=len(self.frame.index)-1
            
        for index in self.frame.index:
            """用for循环区分出盈利交易和亏损交易，并且加入到相应的字典中去"""
            if self.frame.ix[index]["OffsetFlag"]==str(1):
                prices=self.frame.ix[index]["Price"]-self.frame.ix[index-1]["Price"]
                 
                if self.frame.ix[index]["Direction"]==1:
                    prices=prices
                elif self.frame.ix[index]["Direction"]==0:
                    prices=0-prices
                 
                #将所有的成交值放入到一个列表中，方便进行总交易次数和成功率的计算    
                self.time_trade[self.frame.ix[index]["Time"]]=prices
                trade.append(prices)
                #用字典的目的是为了后期盈利曲线的画图
                if prices>0:
                    self.profit[self.frame.ix[index]["Time"]]=prices
                else: 
                    self.loss[self.frame.ix[index]["Time"]]=prices
     
        #交易总盈利
        for time,value in self.profit.items():
            profit_values.append(value)
        self.total_profit=sum(profit_values)*5
#         print(self.profit)
         
        #交易总亏损
        for time,value in self.loss.items():
            loss_values.append(value)
        self.total_loss=sum(loss_values)*5
#         print(self.loss)
         
        #交易净利润
        self.retained_profit=self.total_profit+self.total_loss
         
         
        #总交易次数和成功率
        self.total_tradenumber=len(self.profit)+len(self.loss) #交易总次数
        if self.total_tradenumber !=0:
            self.success_rate="%.2f%%" % (float(len(self.profit))*100/float(self.total_tradenumber)) #交易成功率
         
             
        #最大连续盈利次数和最大连续亏损次数
        for line in range(len(trade)):
            if line==0:
                if trade[line]<0:
                    loss_number +=1
                if trade[line]>0:
                    profit_number +=1
                     
            if line>=1:           
                if trade[line]>0 and trade[line-1]>0: 
                    profit_number +=1
                if trade[line]<0 and trade[line-1]<0:
                    loss_number +=1   
                     
                if trade[line]<0 and trade[line-1]>0:
                    profit_numbers.append(profit_number)
                    profit_number=0
                    loss_number +=1
                if trade[line]>0 and trade[line-1]<0:
                    loss_numbers.append(loss_number)
                    loss_number=0
                    profit_number+=1
            if line==len(trade)-1:
                if profit_number>0:
                    profit_numbers.append(profit_number)
                elif loss_number>0:
                    loss_numbers.append(loss_number)
        self.continuous_profit_number=max(profit_numbers)
        self.continuous_loss_number=max(loss_numbers)
         
         
         
        #交易最大回测
        #需要用到的变量
        self.cumsum_profit=cumsum(trade)
        maximum_switch=False
        maximum_value=0
        minimum_swith=False
        minimum_value=0
        retracement=0
        retracement_list=[]
         
        for i in range(len(self.cumsum_profit)):
            if i>=2:
                if self.cumsum_profit[i-1]>=self.cumsum_profit[i-2] and self.cumsum_profit[i-1]>=self.cumsum_profit[i]:
                    maximum_switch=True
                    retracement=self.cumsum_profit[i-1]-self.cumsum_profit[i]
                    maximum_value=self.cumsum_profit[i-1]
                 
                if maximum_switch==True: 
                    if self.cumsum_profit[i-1] !=maximum_value and self.cumsum_profit[i-1]>=self.cumsum_profit[i]:
                        retracement=retracement+(self.cumsum_profit[i-1]-self.cumsum_profit[i])
                    elif self.cumsum_profit[i-1]<=self.cumsum_profit[i]:
                        retracement_list.append(retracement)
                        retracement=0
                        maximum_switch=False
            if i==len(self.cumsum_profit)-1:
                retracement_list.append(retracement)
         
        self.max_retracement=max(retracement_list)*5
                         
 
        #打印出各个绩效值
         
        print(u"交易净盈利:"+str(self.retained_profit))
        print(u"交易总盈利:"+str(self.total_profit))
        print(u"交易总亏损:"+str(self.total_loss))
        print(u"总交易次数:"+str(self.total_tradenumber))
        print(u"交易成功率:"+str(self.success_rate))
        print(u"最大连续亏损次数:"+str(self.continuous_profit_number))
        print(u"最大连续盈利次数:"+str(self.continuous_loss_number))
        print(u"交易最大回撤:"+str(self.max_retracement))
 
# print(json.dumps(dict, encoding='UTF-8', ensure_ascii=False)) #这一步用于打印有中文字符的字典，视情况决定是否使用
 
        
    def chart_Anlysis(self):
        """图表分析，主要用到matplotlib工具，主要包含以下部分：
        1.绘制权益曲线"""
         
        #绘制权益曲线
        #因为按照字典进行聚合，会出现排序问题，这里经过处理将时间进行提取和排序，主要作为绘图中的X轴
        var=[]
        time_list=[] #最终经过排序能和吻合累计收益的时间列表
        for key,value in self.time_trade.items():
            key=datetime.strptime(key,"%Y/%m/%d %H:%M:%S")
            var.append(key)
        var=sorted(var)
        for i in var:
            i=i.strftime("%Y/%m/%d %H:%M:%S")
            time_list.append(i)
#         d=sorted(key_times.iteritems(),key=lambda asd:asd[0],reverse=False) #对字典进行排序的技巧
 
        #具体的绘图环节，包括设置绘图的各种格式
        self.fig=plt.figure()
        ax1=self.fig.add_subplot(1,1,1)
# #         fig,axes=plt.subplots(2,3)
# #         ax1=axes[0,1] #也可以通过这种方式创建绘图窗口
     
        #也可以使用series或者dataframe结构进行画图，视需求而定
        ax1.plot(self.cumsum_profit,linestyle="--"  ,color="g",marker="o")
        labels=ax1.set_xticklabels(time_list,rotation=10,fontsize="small") #设置X轴为时间
        SD,var1=time_list[0].split(" ") #在图中标题中设置开始日期
        ED,var2=time_list[len(time_list)-1].split(" ") #在图中标题中设置结束日期 
        ax1.set_title("Profit Curve:"+SD+"------"+ED)
        ax1.set_xlabel("Trade Time")
        plt.show()


        
            
    def save_chart(self,address):
        """该方法用于储存绩效图表"""
        self.fig.savefig(address) #自行填入地址

if __name__=="__main__":
    example=TradeData_Analysis()
    example.TradeData_Clean("E:/test.csv")
    example.mathematical_statistics()
    example.chart_Anlysis()