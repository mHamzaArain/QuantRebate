import pandas as pd
from time import sleep
from lightweight_charts import Chart
from datetime import datetime, timedelta

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

symbol = "XLMUSDT"
timeframe = "5m"

conn_ohlc = sqlite3.connect(f'data/{symbol}_{timeframe}_ohlc.db')
conn_tick = sqlite3.connect(f'data/{symbol}_{timeframe}_tick.db')

chart = Chart()

df_ohlc = pd.read_sql_query('SELECT * FROM ohlc_data', conn_ohlc)
# df_ohlc.set_index('time', inplace=True)

df1 = df_ohlc[:400]

df2 = df_ohlc[200:]
# df1 = df_ohlc[:200]
# df1['time'] = pd.to_datetime(df1['time'], unit='ms')

chart.set(df1)

line = chart.create_line()
sma_data = calculate_sma(df1, period=10)
line.set(sma_data, name='SMA 10')

chart.show()

# df_ohlc['time']= pd.to_datetime(df_ohlc['time'])


# last_close = df1.iloc[-1]
# df1.set_index('time', inplace=True)

last_time = df1['time'].iloc[-1]

# print(type(last_time))

for i, series in df2.iterrows():
#     chart.update(series)

#     if check_time_difference(current_time=pd.to_datetime(series['time']), last_time=pd.to_datetime(last_time), interval=5):
#         last_time = series['time']


#     # if series['close'] > 20 and last_close < 20:
#     #     chart.marker(text='The price crossed $20!')
    
#     # last_close = series['close']
    sleep(0.1)

