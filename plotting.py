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

class Essential():
    def __init__(self):
        self.exchange=ccxt.binance()

    async def ohlc_data_fetch(self, symbol='BTCUSDT', timeframe='5m'):
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe)

        dataframe = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        dataframe['time'] = pd.to_datetime(dataframe['time'], unit='ms')
        # df.set_index('timestamp', inplace=True)
        return dataframe

    async def current_price_data(self, symbol):
        data = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}")  
        data = data.json()
        data['time'] = int(time.time())

        dataframe = pd.DataFrame([data])
        dataframe['price'] = dataframe['price'].astype(float)
        dataframe['time'] = pd.to_datetime(dataframe['time'], unit='s')
        dataframe['volume'] = np.nan
        return dataframe
    
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

async def main():
    esn = Essential()

    symbol = 'BNB/USDT'
    tick_symbol = symbol.replace("/", "")
    timeframe = '1m'
    
    timeframe_interval = esn.remove_non_numeric_chars(timeframe)
    df = await esn.ohlc_data_fetch(symbol=symbol, timeframe=timeframe)
    last_time = df['time'].iloc[-1]

    ## tick = await esn.current_price_data(tick_symbol)
    chart = Chart(volume_enabled=False)
    chart.set(df)
    
    df = esn.apply_indicator(df)
    df = esn.buy_screener_condition(df)
    # # line = chart.create_line()

    # # chart.show()
    await chart.show_async()
    
    while True:
        time.sleep(0.1)
        tick = await esn.current_price_data(tick_symbol)
        
        if esn.check_time_difference(current_time=tick['time'], last_time=last_time, interval=timeframe_interval):
            last_time = tick['time']
            df = await esn.ohlc_data_fetch(symbol=symbol, timeframe=timeframe)
            df = esn.apply_indicator(df)
            df = esn.buy_screener_condition(df)
            print(df.tail(3))

        tick=tick.iloc[0,:]

    #     # if series['close'] > 20 and last_close < 20:
    #     #     chart.marker(text='The price crossed $20!')
            
    #     # sma_data = calculate_sma(df)
    #     # line.set(sma_data)
    #     # await 

        chart.update_from_tick(tick)            



if __name__ == '__main__':
    asyncio.run(main())
    # main()

