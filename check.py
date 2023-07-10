import ccxt
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import pandas_ta as ta
import backtrader as bt


exchange = ccxt.binance()

def ohlc_data_fetch(symbol='BTCUSDT', timeframe='5m'):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
    # Eliminate last row
    ohlcv = ohlcv[:-1]
    
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

#calling it a second time may prevent some graphics errors
class SMACrossover(bt.Strategy):
    params = (
        ('ema10', 10),
    )

    def __init__(self):
        self.ema10 = bt.indicators.ExponentialMovingAverage(self.data.close, period=self.params.ema10)
        
                        
    def next(self):
        if self.ema10[0] > self.data.close[0]:
            self.buy()
        elif self.ema10[0] < self.data.close[0]:
            self.sell()

cerebro = bt.Cerebro()

# data = bt.feeds.YahooFinanceData(dataname='AAPL', fromdate=datetime(2019, 1, 1), todate=datetime(2020, 12, 31))
data = ohlc_data_fetch(symbol='BTCUSDT', timeframe='5m')
# data = populate_indicator(data)
feed = bt.feeds.PandasData(dataname=data)
cerebro.adddata(feed)
cerebro.addstrategy(SMACrossover)

cerebro.run()

cerebro.plot()

import freqtrade 