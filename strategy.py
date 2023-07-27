import pandas as pd
import requests
import ccxt
import time
import pandas_ta as ta
from datetime import datetime


class MyAwesomeStrategy:
    def populates_essentials(self):
        return True

    def buy_ohlc_condition(self):
        return True

    def sell_ohlc_condition(self):
        return True

    def buy_tick_condition(self):
        return True

    def sell_tick_condition(self):
        return True



## Interval data
### Last row is current candle that is not made yet so technically 2nd last candle is made 100% not last candle.
def ohlc_data_fetch(symbol='BTCUSDT', timeframe='5m'):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
    # Eliminate last row
    # ohlcv = ohlcv[:-1]
    
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

## Current price data
def current_price_data(pair):
    data = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={pair}")  
    data = data.json()
    data['time'] = int(time.time())
    
    df = pd.DataFrame([data])
    df['price'] = df['price'].astype(float)
    df['time'] = pd.to_datetime(df['time'], unit='ms')

    return df

def apply_indicator(df):
    ## Candle Type
    df['green_candle'] = df['close'] > df['open']
    df['red_candle'] = df['green_candle'] != 1

    ## EMA 10
    df['ema10'] = ta.ema(df.close, timeperiod=10)
    
    ## Shifting
    df['open_n-1'] = df['open'].shift()
    df['high_n-1'] = df['high'].shift()
    df['low_n-1'] = df['low'].shift()
    df['close_n-1'] = df['close'].shift()
    df['ema10_n-1'] = df['ema10'].shift()
    df['green_candle_n-1'] = df['green_candle'].shift()
    df['red_candle_n-1'] = df['red_candle'].shift()

    df['open_n-2'] = df['open'].shift(2)
    df['high_n-2'] = df['high'].shift(2)
    df['low_n-2'] = df['low'].shift(2)
    df['close_n-2'] = df['close'].shift(2)
    df['ema10_n-2'] = df['ema10'].shift(2)
    df['green_candle_n-2'] = df['green_candle'].shift(2)
    df['red_candle_n-2'] = df['red_candle'].shift(2)

    df['open_n-3'] = df['open'].shift(3)
    df['high_n-3'] = df['high'].shift(3)
    df['low_n-3'] = df['low'].shift(3)
    df['close_n-3'] = df['close'].shift(3)
    df['ema10_n-3'] = df['ema10'].shift(3)
    df['green_candle_n-3'] = df['green_candle'].shift(3)
    df['red_candle_n-3'] = df['red_candle'].shift(3)
    return df
    
def buy_screener_condition(dff):
    # 1. Last developed candle is red and completely above 10 ema
    dff['buy_screener_condition_1'] = ( (dff['red_candle']==True) & (dff['low'] > dff['ema10']) )
    
    # 2. 2nd and 3rd last candle is green and completely above 10 ema
    dff['buy_screener_condition_2'] = ( 
                (dff['low_n-1'] > dff['ema10_n-1']) & (dff['low_n-2'] > dff['ema10_n-2']) &\
                (dff['green_candle_n-1']==True) & (dff['green_candle_n-2']==True) 
            ) |\
            (
                (dff['low_n-1'] > dff['ema10_n-1']) & (dff['low_n-2'] > dff['ema10_n-2']) & (dff['low_n-3'] > dff['ema10_n-3'])&\
                (dff['green_candle_n-1']==False) & (dff['green_candle_n-2']==True) & (dff['green_candle_n-3']==True) 
            )
    # 3. Buy condition
    dff['buy_screener_conditions_all'] = (dff['buy_screener_condition_1'] & dff['buy_screener_condition_2'])
    
    # Either True/False
    value = dff['buy_screener_conditions_all'].iloc[-1]
    
    return value, dff

def buy_active_condition(symbol):
    # 1. Current price >= -> 1. Last developed candle is red and completely above 10 ema
    new_data = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.replace('/', '')}")  
    new_data = new_data.json()
    new_data['price'] = float(new_data['price'])
    # new_data['time'] = int(time.time())
    return new_data
    
def calculate_entry_tp_sl(buy_size_usd, entry_base_currency, stoploss, rr=2.5):
    # 1. Calculate qty of base aginst quote pair (e.g; BTC/USDT how many qty of BTC we get from 50 USDT.)
    qty_base_currency = buy_size_usd / entry_base_currency
    
    # 2. Calculate stoploss
    ## For now @ 10 ema of last red candle -> 1. Last developed candle is red and completely above 10 ema
    stoploss_base_currency = stoploss
    
    # 3. Take Profit
    ## Takeprofit 1:2.5 RR
    risk_usd = entry_base_currency - stoploss_base_currency 
    reward_usd = risk_usd*rr
    takeprofit = entry_base_currency + reward_usd
    
    return qty_base_currency, stoploss_base_currency, takeprofit

def buy():
    # https://stackoverflow.com/questions/65551059/how-to-send-oco-order-to-binance
    ## Buy
    order = exchange.create_order(symbol, 'limit', 'buy', amount, price)  # initial opening order
    print(order)
    
    # Sell 
    order= client.order_oco_sell(
        symbol= 'BTCUSDT',                                            
        quantity= 1.00000,                                            
        price= '32000.07',                                            
        stopPrice= '29283.03',                                            
        stopLimitPrice= '29000.00',                                            
        stopLimitTimeInForce= 'FOK')
    
    print(order)
    
def check_sell_codition_price(takeprofit, stoploss):
    # This will check that orders are executing successfully because STOP LIMIT ORDER handle sl and tp itself.
    pass
    
def calculate_pnl():
    # Calculate PNL of each trade
    pass


exchange = ccxt.binance()
symbol = 'BNB/USDT'
timeframe = '5m'

def strategy(pair, tf, open_position=False):
    while True:
        df = ohlc_data_fetch(symbol=pair, timeframe=tf)
        df = apply_indicator(df)
        print(df.iloc[-1])
        # 0. Check position is not active.
        if not open_position:
            # 1. Screener will check that bot should active from given condition
            screener_condition, df = buy_screener_condition(df)

            if screener_condition:
                not_bought_yet = True
                last_candle_time = df.index[-1]
                expiry_time = int(time.mktime(t.timetuple()))+300
                previos_candle_open = df['open'].iloc[-1]
                while not_bought_yet:
                    # 2. If screener condition satisfied, now check buy condition on active price.
                    new_data = buy_active_condition(pair, previos_candle_open)
                    if df['open'] >= new_data['price'] and df['low'] > df['ema10']:
                        # 3. Calculate entry price, take profit stoploss and qty of base against quote.
                        entry_price, tp, sl, qty = calculate_entry_tp_sl(buy_size_usd=20, entry_base_currency=new_data['price'], stoploss=df['open'].iloc[-1], rr=2.5) 
                        # 4. If buy condition condition satisfied, then BUY @ STOP BUY ORDER
                        # buy()
                        print("entry_price: ", entry_price)
                        print("tp: ", tp)
                        print("sl: ", sl)
                        print("qty: ", qty)
                        not_bought_yet = False
                    elif df['low'] < df['ema10']:
                        not_bought_yet = False
                    elif time.time() < last_candle_time:
                        df = ohlc_data_fetch(symbol=pair, timeframe=tf)
                        df = apply_indicator(df)
                    elif time.time() > expiry_time:
                        not_bought_yet = False  
                        
            else:
                time.sleep(60)
        
        # 5. Check position is active.
        if open_position:
            # 6. Check current price hit stoploss and check position is cleared?
            check_sell_codition_price()
            
            # 7. Calculate PNL
            
strategy('BNBUSDT', "5m")

# df = ohlc_data_fetch(symbol=symbol, timeframe=timeframe)
# df = apply_indicator(df)
# screener_condition, df = buy_screener_condition(df)
# print(screener_condition)
