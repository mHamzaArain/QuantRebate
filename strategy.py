import pandas_ta as ta


class MyAwesomeStrategy:
    def populate_essentials(self, dataframe):
        dataframe['sma10'] = ta.sma(dataframe.close, timeperiod=10)
        dataframe['green_candle'] = dataframe['close'] > dataframe['open']
        dataframe['red_candle'] = dataframe['green_candle'] != 1
        return dataframe

    def buy_ohlc_condition(self, dataframe):
        dataframe['buy_screener_condition_1'] = ( (dataframe['red_candle']==True) & (dataframe['low'] > dataframe['ema10']) )

        dataframe['buy_ohlc_condition'] = (dataframe['green_candle'])
        return True

    def sell_ohlc_condition(self, dataframe):
        return True

    def buy_tick_condition(self):
        return True

    def sell_tick_condition(self):
        return True

