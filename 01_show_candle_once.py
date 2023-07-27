import pandas as pd
from time import sleep
from lightweight_charts import Chart
import sqlite3
import numpy as np


def calculate_sma(data: pd.DataFrame, period: int = 50):
    def avg(d: pd.DataFrame):
        return d['close'].mean()
    result = []
    for i in range(period - 1, len(data)):
        val = avg(data.iloc[i - period + 1:i])
        result.append({'date': data.iloc[i]['date'], f'SMA {period}': val})
    return pd.DataFrame(result)

if __name__ == '__main__':
    chart = Chart()

    df = pd.read_csv('data/ohlcv_manupulated.csv')

    ## Chart
    chart.set(df)
    chart.precision(6)

    # ## Line
    period = 10
    line = chart.create_line()
    sma_data = calculate_sma(df, period)
    line.set(sma_data, name='SMA 10')

    ## Chart
    chart.show(block=True)

