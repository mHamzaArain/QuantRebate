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

if __name__ == '__main__':
    ## Essentials
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
    df2 = df_ohlc[:end_time]
    df3 = df_tick[start_time:end_time]

    df1.reset_index(inplace=True)
    df3.reset_index(inplace=True)
    df3['volume'] = [0 for i in range(df3.shape[0])]

    ## Chart
    chart = Chart()
    chart.set(df1)
    chart.precision(6)

    ## Line
    period = 10
    line = chart.create_line()
    sma_data = calculate_sma(df1, period)
    line.set(sma_data, name='SMA 10')

    ## Chart
    # chart.show(block=True)
    chart.show()

    last_time = df1['time'].iloc[-1]


    for i, series in df3.iterrows():
        if check_time_difference(current_time=pd.to_datetime(series['time']), last_time=pd.to_datetime(last_time), interval=5):
            last_time = series['time']
            df = df2[:last_time].copy()
            df.reset_index(inplace=True)

            recalculated_sma = calculate_sma(df, period)
            line_value = recalculated_sma.iloc[-1]
            line.update(line_value.rename({'SMA 10': 'value'}))
            sleep(0.1)
        chart.update_from_tick(series)
