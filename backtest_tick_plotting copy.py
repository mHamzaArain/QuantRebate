import pandas as pd
from time import sleep
from lightweight_charts import Chart
from datetime import datetime, timedelta
import numpy as np
import pandas_ta as ta


import sqlite3

def calculate_sma(data: pd.DataFrame, period: int = 50):
    def avg(d: pd.DataFrame):
        return d['close'].mean()
    result = []
    for i in range(period - 1, len(data)):
        val = avg(data.iloc[i - period + 1:i])
        result.append({'time': data.iloc[i]['time'], f'SMA {period}': val})
    return pd.DataFrame(result)

def check_time_difference(current_time, last_time, interval):
    time_difference = current_time - last_time
    if (time_difference >= timedelta(minutes=interval)):
        return True
    else:
        return False
    
def apply_indicator(dataframe):
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

symbol = "LINAUSDT"
timeframe = "5m"

conn_ohlc = sqlite3.connect(f'data/{symbol}_{timeframe}_ohlc.db')
conn_tick = sqlite3.connect(f'data/{symbol}_{timeframe}_tick.db')

df_ohlc = pd.read_sql_query('SELECT * FROM ohlc_data', conn_ohlc)
df_ohlc['time']= pd.to_datetime(df_ohlc['time'])
df_ohlc.set_index('time', inplace=True)
df_ohlc.drop_duplicates(inplace=True)

df_tick = pd.read_sql_query('SELECT * FROM tick_data', conn_tick)
df_tick['time']= pd.to_datetime(df_tick['time'])
df_tick.set_index('time', inplace=True)


start_time = "2023-07-22 03:59:03"
end_time = "2023-07-23 12:29:41"
beyond_time = start_time

df1 = df_ohlc[:start_time]
df2 = df_ohlc[start_time:end_time]
df3 = df_tick[start_time:end_time]

df1.reset_index(inplace=True)
df3.reset_index(inplace=True)
df3['volume'] = [0 for i in range(df3.shape[0])]


chart = Chart()

chart.set(df1)

line = chart.create_line()
sma_data = calculate_sma(df1, period=10)
line.set(sma_data, name='SMA 10')

chart.show()

# # df_ohlc['time']= pd.to_datetime(df_ohlc['time'])


# last_close = df1.iloc[-1]
# df1.set_index('time', inplace=True)

last_time = df1['time'].iloc[-1]

# print(type(last_time))

for i, series in df3.iterrows():
#     chart.update(series)

    if check_time_difference(current_time=pd.to_datetime(series['time']), last_time=pd.to_datetime(last_time), interval=5):
        last_time = series['time']
        # print(last_time)

        df = df_ohlc[:last_time].copy()
        df.reset_index(inplace=True)
        sma_data = calculate_sma(df, period=10)


    # if series['price'] >  and last_close < 20:
    #     chart.marker(text='The price crossed $20!')
    
#     # last_close = series['close']
    chart.update_from_tick(series)   
    # sleep(1)
         
    # sleep(0.000001)

