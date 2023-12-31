import pandas as pd
from time import sleep
from lightweight_charts import Chart
import sqlite3

from strategy import MyAwesomeStrategy

def calculate_sma(data: pd.DataFrame, period: int = 50):
    def avg(d: pd.DataFrame):
        return d['close'].mean()
    result = []
    for i in range(period - 1, len(data)):
        val = avg(data.iloc[i - period + 1:i])
        result.append({'time': data.iloc[i]['time'], f'SMA {period}': val})
    return pd.DataFrame(result)

if __name__ == '__main__':
    ## Essentials
    symbol = "LINAUSDT"
    timeframe = "5m"
    conn_ohlc = sqlite3.connect(f'data/{symbol}_{timeframe}_ohlc.db')
    df_ohlc = pd.read_sql_query('SELECT * FROM ohlc_data', conn_ohlc)
    
    # print(df_ohlc)

    df1 = df_ohlc[:100]

    my_strategy = MyAwesomeStrategy()
    df_ohlc = my_strategy.populate_essentials(dataframe=df_ohlc)
    df_ohlc = my_strategy.buy_ohlc_condition(dataframe=df_ohlc)

    df2 = df_ohlc[100:]
    period = 10

    # Chart
    chart = Chart()
    chart.set(df1)
    chart.precision(6)

    ## Line
    line = chart.create_line()
    sma_data = calculate_sma(df1, period)
    line.set(sma_data, name='SMA 10')

    # Chart
    chart.show(block=False)

    for i, series in df2.iterrows():
        if series['buy_ohlc_condition']:
            chart.marker(text='', position='below', shape= 'arrow_up', color= '#2196F3')

        chart.update(series[['time', 'open', 'high', 'low', 'close', 'volume']])
        recalculated_sma = calculate_sma(df_ohlc[:i+1], period)
        line_value = recalculated_sma.iloc[-1]
        line.update(line_value.rename({'SMA 10': 'value'}))
        sleep(0.1)