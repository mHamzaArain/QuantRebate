import ccxt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates

exchange = ccxt.binance()
symbol = 'BTC/USDT'

def get_latest_candles(symbol, timeframe='1m', limit=300):
    candles = exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def plot_support_resistance(df, ax):
    # Calculate pivot points
    pivot_high = df['high'].rolling(5).max()
    pivot_low = df['low'].rolling(5).min()

    # Calculate resistance and support levels
    resistance1 = (2 * pivot_high + df['low'].rolling(5).min()) / 3
    support1 = (2 * pivot_low + df['high'].rolling(5).max()) / 3

    # Plot the levels
    ax.plot(df['timestamp'], resistance1, color='orange', linestyle='--', label='Resistance 1')
    ax.plot(df['timestamp'], support1, color='blue', linestyle='--', label='Support 1')


    # Add legend and grid
    ax.legend()
    ax.grid(True)



def update_plot(frame, ax, ax2, ax3):
    df = get_latest_candles(symbol)
    ax.clear()
    ax.xaxis_date()
    ax.set_title(symbol)
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    ax.grid(True)



    for i in range(len(df)):
        # Calculate the midpoint of the candlestick
        mid = (df['open'][i] + df['close'][i]) / 2.0

        # Calculate the height of the candlestick
        height = abs(df['close'][i] - df['open'][i])

        # Plot the high and low prices as vertical lines
        ax.vlines(df['timestamp'][i], df['low'][i], df['high'][i], color='black', linewidth=1)

        # Plot the open and close prices as filled rectangles
        if df['open'][i] > df['close'][i]:
            ax.fill_betweenx([mid - height / 2, mid + height / 2], df['timestamp'][i], df['timestamp'][i] + pd.Timedelta(minutes=1), facecolor='red', alpha=0.5)
        else:
            ax.fill_betweenx([mid - height / 2, mid + height / 2], df['timestamp'][i], df['timestamp'][i] + pd.Timedelta(minutes=1), facecolor='green', alpha=0.5)

    # plot_support_resistance(df, ax)

    # Calculate EMA5
    ema = df['close'].ewm(span=5, adjust=False).mean()
    ax.plot(df['timestamp'], ema, color='blue', linewidth=2)

    # Plot volume bars
    ax2.clear()
    ax2.bar(df['timestamp'], df['volume'], width=0.001, align='center')
    ax2.set_ylabel('Volume')

    # Calculate EMA5 of volume
    ema_vol = df['volume'].ewm(span=5, adjust=False).mean()
    ax3.clear()
    ax3.plot(df['timestamp'], ema_vol, color='blue', linewidth=2)
    ax3.set_ylabel('EMA5 of Volume')


def main():
    fig = plt.figure(figsize=(12, 8))
    ax = plt.subplot2grid((4,4), (0,0), rowspan=3, colspan=4)
    ax2 = plt.subplot2grid((4,4), (3,0), rowspan=1, colspan=4, sharex=ax)
    ax3 = ax2.twinx()

    ani = animation.FuncAnimation(fig, update_plot, fargs=(ax, ax2, ax3), interval=1000)
    plt.show()

if __name__ == '__main__':
    main()





