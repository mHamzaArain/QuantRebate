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
import strategy



class API():
    def __init__(self):
        self.exchange=ccxt.binance()

    async def ohlc_data_fetch(self, symbol='BTCUSDT', timeframe='5m'):
        while True:
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe)
                dataframe = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
                dataframe['time'] = pd.to_datetime(dataframe['time'], unit='ms')
                return dataframe
            except:
                time.sleep(3)
                
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

class Tools:
    def __init__(self, symbol, timeframe):
        self.without_slash_symbol = self.remove_slash_from_pair(symbol=symbol)  # "BTC/USDT" -> "BTCUSDT"
        self.int_timeframe = self.remove_non_numeric_chars(string=timeframe)    # "5m" -> 5

    def remove_non_numeric_chars(self, string):
        return int(re.sub(r'\D', '', string))

    def remove_slash_from_pair(self, symbol):
        return symbol.replace("/", "")

    def check_time_difference(self, current_time, last_time):
        time_difference = current_time - last_time
        if (time_difference >= timedelta(minutes=self.int_timeframe))[0]:
            return True
        else:
            return False
    
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

class Indicators:
    def calculate_sma(self, data: pd.DataFrame, period: int = 10):
        def avg(d: pd.DataFrame):
            return d['close'].mean()
        result = []
        for i in range(period - 1, len(data)):
            val = avg(data.iloc[i - period + 1:i])
            result.append({'time': data.iloc[i]['time'], f'SMA {period}': val})
        return pd.DataFrame(result)


class Database:
    def to_db(self, dataframe, db_table,  connection):
        dataframe.to_sql(db_table, connection, if_exists='append', index=False)


async def main(symbol, timeframe):
    # Initilize api
    api = API()

    ## 
    tool = Tools(symbol=symbol, timeframe=timeframe)

    # Get ohlcv data
    df = await api.ohlc_data_fetch(symbol=symbol, timeframe=timeframe)
    last_time = df['time'].iloc[-1]

    # Chart
    chart = Chart(volume_enabled=False)
    chart.set(df)


    # Line 
    indicator = Indicators()

    period=10
    line = chart.create_line()
    sma_data = indicator.calculate_sma(df, period=10)
    line.set(sma_data, name='SMA 10')

    # Initialize Strategy
    strat = strategy.MyAwesomeStrategy()

    chart.show()

    while True:
        # Get tick data
        tick = await api.current_price_data(symbol=tool.without_slash_symbol)

        # Check timeframe intervale passed 
        if tool.check_time_difference(current_time=tick['time'], last_time=last_time):
            # Update last_time
            last_time = tick['time']

            # Get ohlcv data
            df = await api.ohlc_data_fetch(symbol=symbol, timeframe=timeframe)

            recalculated_sma =  indicator.calculate_sma(df, period)
            line_value = recalculated_sma.iloc[-1]
            line.update(line_value.rename({'SMA 10': 'value'}))

        ## Buy 
        if strat.buy_ohlc_condition():

            ## Calculate qty, sl, tp

            ## Buy Limit

            ## Chart update


            pass

        tick=tick.iloc[0,:]
        chart.update_from_tick(tick)            
        time.sleep(0.1)




if __name__=="__main__":
    symbol = "BTC/USDT"
    timeframe = "1m"

    asyncio.run(main(symbol=symbol, timeframe=timeframe))
