#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from talib.abstract import SMA
import numpy as np
from collections import deque
from gmsdk import *

# 绠楁硶鐢ㄥ埌鐨勪竴浜涘父閲忥紝闃�鍊硷紝涓昏鐢ㄤ簬淇″彿杩囨护
eps = 1e-6
threshold = 0.235
tick_size = 0.2
half_tick_size = tick_size / 2
significant_diff = tick_size * 2.6

class MA(StrategyBase):

    ''' strategy example1: MA decision price cross long MA, then place a order, temporary reverse trends place more orders '''

    def __init__(self, *args, **kwargs):
        #import pdb; pdb.set_trace()
        super(MA, self).__init__(*args, **kwargs)
        # 绛栫暐鍒濆鍖栧伐浣滃湪杩欓噷鍐欙紝浠庡閮ㄨ鍙栭潤鎬佹暟鎹紝璇诲彇绛栫暐閰嶇疆鍙傛暟绛夊伐浣滐紝鍙湪绛栫暐鍚姩鍒濆鍖栨椂鎵ц涓�娆°��

        # 浠庨厤缃枃浠朵腑璇诲彇閰嶇疆鍙傛暟
        self.exchange = self.config.get('para', 'trade_exchange')
        self.sec_id = self.config.get('para', 'trade_symbol')
        self.symbol = ".".join([self.exchange, self.sec_id])
        self.last_price = 0.0
        self.trade_unit = [1.0, 2.0, 4.0, 8.0, 5.0, 3.0,2.0,1.0,1.0, 0.0] ##  [8.0, 4.0, 2.0, 1.0]
        self.trade_count = 0
        self.trade_limit = len(self.trade_unit)
        self.window_size = self.config.getint('para', 'window_size') or 60
        self.timeperiod = self.config.getint('para', 'timeperiod') or 60
        self.bar_type = self.config.getint('para', 'bar_type') or 15
        self.close_buffer = deque(maxlen=self.window_size)
        self.significant_diff = self.config.getfloat('para', 'significant_diff') or significant_diff

        # prepare historical bars for MA calculating
        # 浠庢暟鎹湇鍔′腑鍑嗗涓�娈靛巻鍙叉暟鎹紝浣垮緱鏀跺埌绗竴涓猙ar鍚庡氨鍙互鎸夐渶瑕佽绠梞a
        last_closes = [bar.close for bar in self.get_last_n_bars(self.symbol, self.bar_type, self.window_size)]
        last_closes.reverse()     #鍥犱负鏌ヨ鍑烘潵鐨勬椂闂存槸鍊掑簭鎺掑垪锛岄渶瑕佸�掍竴涓嬮『搴�
        self.close_buffer.extend(last_closes)

    # 鍝嶅簲bar鏁版嵁鍒拌揪浜嬩欢
    def on_bar(self, bar):
        # 纭涓媌ar鏁版嵁鏄闃呯殑鍒嗘椂
        if bar.bar_type == self.bar_type:
            # 鎶婃暟鎹姞鍏ョ紦瀛�
            self.close_buffer.append(bar.close)
            # 璋冪敤绛栫暐璁＄畻
            self.algo_action()

   # 鍝嶅簲tick鏁版嵁鍒拌揪浜嬩欢
    def on_tick(self, tick):
        # 鏇存柊甯傚満鏈�鏂版垚浜や环
        self.last_price = tick.last_price

    def on_execution(self, execution):
        #鎵撳嵃璁㈠崟鎴愪氦鍥炴姤淇℃伅
        print "received execution: %s" % execution.exec_type

    #绛栫暐鐨勭畻娉曞嚱鏁帮紝绛栫暐鐨勪氦鏄撻�昏緫瀹炵幇閮ㄥ垎
    def algo_action(self):
        #鏁版嵁杞崲锛屾柟渚胯皟鐢╰a-lib鍑芥暟杩涜鎶�鏈寚鏍囩殑璁＄畻锛岃繖閲岀敤SMA鎸囨爣
        close = np.asarray(self.close_buffer)
        ma = SMA({'close':close}, timeperiod=self.timeperiod)
        delta = round(close[-1] - ma[-1],4)     # 鏈�鏂版暟鎹偣锛宐ar鐨勬敹鐩樹环璺焟a鐨勫樊
        last_ma = round(ma[-1], 4)  #  鍧囩嚎ma鐨勬渶鏂板��
        momentum = round(self.last_price - last_ma,4)  # 褰撳墠鏈�鏂颁环鏍艰窡ma涔嬮棿鐨勫樊锛屾垚浜や环鐩稿ma鍋忕
        #print 'close: ', close
        print('close ma delta: {0}, last_ma: {1}, momentum: {2}'.format(delta, last_ma, momentum))

        a_p = self.get_position(self.exchange, self.sec_id, OrderSide_Ask)    #鏌ヨ绛栫暐鎵�鎸佹湁鐨勭┖浠�
        b_p = self.get_position(self.exchange, self.sec_id, OrderSide_Bid)    #鏌ヨ绛栫暐鎵�鎸佹湁鐨勫浠�
        # 鎵撳嵃鎸佷粨淇℃伅
        print ('pos long: {0} vwap: {1}, pos short: {2}, vwap: {3}'.format(b_p.volume if b_p else 0.0,
                round(b_p.vwap,2) if b_p else 0.0,
                a_p.volume if a_p else 0.0,
                round(a_p.vwap,2) if a_p else 0.0))
        if delta > threshold and momentum >= significant_diff:        ## 鏀剁洏浠蜂笂绌垮潎绾匡紝涓斿綋鍓嶄环鏍煎亸绂绘弧瓒抽棬闄愯繃婊ゆ潯浠讹紝澶氫俊鍙�
            # 娌℃湁绌轰粨锛屼笖娌℃湁瓒呭嚭涓嬪崟娆℃暟闄愬埗
            if (a_p is None or a_p.volume < eps) and self.trade_count < self.trade_limit:
                # 渚濇鑾峰彇涓嬪崟鐨勪氦鏄撻噺锛屼笅鍗曢噺鏄厤缃殑涓�涓暣鏁版暟鍒楋紝鐢ㄤ簬浠撲綅绠＄悊锛屽彲鐢ㄩ厤缃枃浠朵腑璁剧疆
                vol = self.trade_unit[self.trade_count]
                # 濡傛灉鏈涓嬪崟閲忓ぇ浜�0,  鍙戝嚭涔板叆濮旀墭浜ゆ槗鎸囦护
                if vol > eps:
                    self.open_long(self.exchange, self.sec_id, self.last_price, vol)
                self.trade_count += 1    #澧炲姞璁℃暟
            else:
                #  濡傛灉鏈夌┖浠擄紝涓旇揪鍒版湰娆′俊鍙风殑浜ゆ槗娆℃暟涓婇檺
                if a_p and a_p.volume > eps and self.trade_count == self.trade_limit:
                    self.close_short(self.exchange, self.sec_id, self.last_price, a_p.volume)    # 骞虫帀鎵�鏈夌┖浠�
                    self.trade_count = 0
                else:
                    # 鏈夌┖浠撴椂锛屼笖涓婃浜ゆ槗淇″彿鍚庢病杈惧埌浜ゆ槗娆℃暟闄愬埗锛岀户缁姞绌�
                    vol = self.trade_unit[self.trade_count] if self.trade_count < self.trade_limit else 0.0
                    self.trade_count += 1
                    if vol > eps:
                        self.open_short(self.exchange, self.sec_id,self.last_price, vol)
        elif delta < -threshold and momentum <= - significant_diff:     ## bar 鏀剁洏浠蜂笅绌縨a鍧囩嚎锛屼笖鍋忕婊¤冻淇″彿杩囨护鏉′欢
            # 娌℃湁澶氫粨鏃讹紝寮�绌�
            if (b_p is None or b_p.volume < eps) and self.trade_count < self.trade_limit:
                vol = self.trade_unit[self.trade_count]
                self.trade_count += 1
                if vol > eps:
                    self.open_short(self.exchange, self.sec_id, self.last_price, vol)
            else:
                # 宸叉湁澶氫粨锛屼笖杈惧埌浜嗕氦鏄撴鏁伴檺鍒讹紝骞虫帀澶氫粨
                if b_p and b_p.volume > eps and self.trade_count == self.trade_limit:
                    self.close_long(self.exchange, self.sec_id, self.last_price, b_p.volume)
                    self.trade_count = 0
                else:
                    # 宸叉湁澶氫粨锛屼笖娌℃湁杈惧埌浜ゆ槗娆℃暟闄愬埗锛岀户缁姞澶�
                    vol = self.trade_unit[self.trade_count] if self.trade_count < self.trade_limit else 0.0
                    self.trade_count += 1
                    if vol > eps:
                        self.open_long(self.exchange, self.sec_id, self.last_price, vol)
        else:       ##  鍏朵粬鎯呭喌锛屽拷鐣ヤ笉澶勭悊
            ## get positions and close if any
            #self.trade_count = 0   ## reset trade count
            pass

# 绛栫暐鍚姩鍏ュ彛
if __name__ == '__main__':
    #  鍒濆鍖栫瓥鐣�
    ma = MA(config_file='dual_ma.ini')
    #import pdb; pdb.set_trace()   # python璋冭瘯寮�鍏�
    print 'strategy ready, waiting for market data ......'
    # 绛栫暐杩涘叆杩愯锛岀瓑寰呮暟鎹簨浠�
    ret = ma.run()
    # 鎵撳嵃绛栫暐閫�鍑虹姸鎬�
    print "MA :", ma.get_strerror(ret)

