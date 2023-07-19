import pandas as pd
from lightweight_charts import Chart
import ccxt
import requests
import time
import numpy as np
import asyncio
import pandas_ta as ta
from datetime import datetime, timedelta
import re
import sqlite3

class Essential():
    def __init__(self):
        self.exchange=ccxt.binance()

    async def ohlc_data_fetch(self, symbol='BTCUSDT', timeframe='5m'):
        while True:
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe)

                dataframe = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
                dataframe['time'] = pd.to_datetime(dataframe['time'], unit='ms')
                # df.set_index('timestamp', inplace=True)
                return dataframe
            except:
                time.sleep(3)
                pass
    async def current_price_data(self, symbol):
        while True:
            try:
                data = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}")  
                data = data.json()
                data['time'] = int(time.time())

                dataframe = pd.DataFrame([data])
                dataframe['price'] = dataframe['price'].astype(float)
                dataframe['time'] = pd.to_datetime(dataframe['time'], unit='s')
                dataframe['volume'] = np.nan
                return dataframe
                
            except:
                time.sleep(1)
                pass


    def check_time_difference(self, current_time, last_time, interval):
        time_difference = current_time - last_time
        # print(time_difference, " ",interval )
        if (time_difference >= timedelta(minutes=interval))[0]:
            return True
        else:
            return False
    
    def remove_non_numeric_chars(self, string):
        return int(re.sub(r'\D', '', string))

    def apply_indicator(self, dataframe):
        ## Candle Type
        dataframe['green_candle'] = dataframe['close'] > dataframe['open']
        dataframe['red_candle'] = dataframe['green_candle'] != 1

        ## EMA 10
        dataframe['ema10'] = ta.ema(dataframe.close, timeperiod=10)
        
        ## Shifting
        dataframe['open_n-1'] = dataframe['open'].shift()
        dataframe['high_n-1'] = dataframe['high'].shift()
        dataframe['low_n-1'] = dataframe['low'].shift()
        dataframe['close_n-1'] = dataframe['close'].shift()
        dataframe['ema10_n-1'] = dataframe['ema10'].shift()
        dataframe['green_candle_n-1'] = dataframe['green_candle'].shift()
        dataframe['red_candle_n-1'] = dataframe['red_candle'].shift()

        dataframe['open_n-2'] = dataframe['open'].shift(2)
        dataframe['high_n-2'] = dataframe['high'].shift(2)
        dataframe['low_n-2'] = dataframe['low'].shift(2)
        dataframe['close_n-2'] = dataframe['close'].shift(2)
        dataframe['ema10_n-2'] = dataframe['ema10'].shift(2)
        dataframe['green_candle_n-2'] = dataframe['green_candle'].shift(2)
        dataframe['red_candle_n-2'] = dataframe['red_candle'].shift(2)

        dataframe['open_n-3'] = dataframe['open'].shift(3)
        dataframe['high_n-3'] = dataframe['high'].shift(3)
        dataframe['low_n-3'] = dataframe['low'].shift(3)
        dataframe['close_n-3'] = dataframe['close'].shift(3)
        dataframe['ema10_n-3'] = dataframe['ema10'].shift(3)
        dataframe['green_candle_n-3'] = dataframe['green_candle'].shift(3)
        dataframe['red_candle_n-3'] = dataframe['red_candle'].shift(3)
        return dataframe

    def buy_screener_condition(self, dataframe):
        # 1. Last developed candle is red and completely above 10 ema
        dataframe['buy_screener_condition_1'] = ( (dataframe['red_candle']==True) & (dataframe['low'] > dataframe['ema10']) )
        
        # 2. 2nd and 3rd last candle is green and completely above 10 ema
        dataframe['buy_screener_condition_2'] = ( 
                    (dataframe['low_n-1'] > dataframe['ema10_n-1']) & (dataframe['low_n-2'] > dataframe['ema10_n-2']) &\
                    (dataframe['green_candle_n-1']==True) & (dataframe['green_candle_n-2']==True) 
                ) |\
                (
                    (dataframe['low_n-1'] > dataframe['ema10_n-1']) & (dataframe['low_n-2'] > dataframe['ema10_n-2']) & (dataframe['low_n-3'] > dataframe['ema10_n-3'])&\
                    (dataframe['green_candle_n-1']==False) & (dataframe['green_candle_n-2']==True) & (dataframe['green_candle_n-3']==True) 
                )
        # 3. Buy condition
        dataframe['buy_screener_conditions_all'] = (dataframe['buy_screener_condition_1'] & dataframe['buy_screener_condition_2'])
        
        return dataframe
    
    def calculate_entry_tp_sl(self, buy_size_usd, entry_base_price, stoploss, rr=2.5):
        # 1. Calculate qty of base aginst quote pair (e.g; BTC/USDT how many qty of BTC we get from 50 USDT.)
        qty_base_currency = buy_size_usd / entry_base_price
        
        # 2. Calculate stoploss
        ## For now @ 10 ema of last red candle -> 1. Last developed candle is red and completely above 10 ema
        stoploss_base_price = stoploss
        
        # 3. Take Profit
        ## Takeprofit 1:2.5 RR
        risk_usd = entry_base_price - stoploss_base_price 
        reward_usd = risk_usd*rr
        takeprofit = entry_base_price + reward_usd
        
        return qty_base_currency, stoploss_base_price, takeprofit
    
    def to_db(self, dataframe, db_table,  connection):
        dataframe.to_sql(db_table, connection, if_exists='append', index=False)


async def main():
    esn = Essential()
    symbol = 'XRP/USDT'

    tick_symbol = symbol.replace("/", "")
    timeframe = '5m'
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn_ohlc = sqlite3.connect(f'data/{tick_symbol}_{timeframe}_ohlc.db')
    conn_tick = sqlite3.connect(f'data/{tick_symbol}_{timeframe}_tick.db')

    timeframe_interval = esn.remove_non_numeric_chars(timeframe)
    df = await esn.ohlc_data_fetch(symbol=symbol, timeframe=timeframe)
    last_time = df['time'].iloc[-1]

    # tick = await esn.current_price_data(tick_symbol)
    chart = Chart(volume_enabled=False)
    # chart.layout(background_color="rgba(0, 0, 0, 0.07)")
    # chart.candle_style(down_color="rgba(0, 0, 0, 1)")
    chart.set(df)
    
    df = esn.apply_indicator(df)
    df = esn.buy_screener_condition(df)
    condition_satisfied_once = True
    is_bought = False
    # # line = chart.create_line()

    # # chart.show()
    await chart.show_async()
    df.to_sql('ohlc_data', conn_ohlc, if_exists='append', index=False)


    while True:
        time.sleep(0.1)
        tick = await esn.current_price_data(tick_symbol)
        
        if esn.check_time_difference(current_time=tick['time'], last_time=last_time, interval=timeframe_interval):
            last_time = tick['time']
            df = await esn.ohlc_data_fetch(symbol=symbol, timeframe=timeframe)
            try:
                esn.to_db(dataframe=df, db_table='ohlc_data', connection=conn_ohlc)
            except:
                time.sleep(0.3)
                df = await esn.ohlc_data_fetch(symbol=symbol, timeframe=timeframe)
                esn.to_db(dataframe=df, db_table='ohlc_data', connection=conn_ohlc)

            df = esn.apply_indicator(df)
            df = esn.buy_screener_condition(df)
            condition_satisfied_once = True
            # print(df.tail(3))
            print(df[['ema10', "red_candle", "buy_screener_condition_1", "buy_screener_condition_2", "buy_screener_conditions_all"]].tail(5))

        # print(tick['price'][0])
        # print(df['ema10'].iloc[-1])
        # line = chart.create_line()
        
        # if tick['price'][0] > df['buy_screener_conditions_all'].iloc[-1] and condition_satisfied_once:
        if df['buy_screener_conditions_all'].iloc[-1] and tick['price'][0] >= df['open'].iloc[-1] and df['low'].iloc[-1] > df['ema10'].iloc[-1] and condition_satisfied_once and is_bought==False:
            qty, sl, tp = esn.calculate_entry_tp_sl(buy_size_usd=50, entry_base_price=df['low'].iloc[-2], stoploss=df['low'].iloc[-1], rr=2.5)
            chart.marker(text='buy')
            is_bought = True
            condition_satisfied_once = False

            chart.horizontal_line(price=tick['price'][0], color="blue", width=1, style='dotted', text="Entry")
            chart.horizontal_line(price=tp, color="green", width=2, style='large_dashed', text="TP")
            chart.horizontal_line(price=sl, color="red", width=2, style='large_dashed', text="SL")

            print("EP: ", tick['price'][0])
            print("TP: ", tp)
            print("SL: ", sl)

            img = chart.screenshot()
            with open(f"data/{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_{timeframe}.png", 'wb') as f:
                f.write(img)
        
        esn.to_db(dataframe=tick, db_table='tick_data', connection=conn_tick)


        tick=tick.iloc[0,:]
    #     # sma_data = calculate_sma(df)
    #     # line.set(sma_data)
    #     # await 

        chart.update_from_tick(tick)            


if __name__ == '__main__':
    asyncio.run(main())

