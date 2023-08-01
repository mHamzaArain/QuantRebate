import pandas_ta as ta


class MyAwesomeStrategy:
    def populate_essentials(self, dataframe):
        dataframe['sma10'] = ta.sma(dataframe.close, timeperiod=10)
        dataframe['green_candle'] = dataframe['close'] > dataframe['open']
        dataframe['red_candle'] = dataframe['green_candle'] != 1
        return dataframe

    def buy_ohlc_condition(self, dataframe):
        # This is not valid for ticker and realtime data
        dataframe['tick_condition'] = ( (dataframe['high'].shift() <= dataframe['open']) | (dataframe['high'].shift() <= dataframe['high']) | (dataframe['high'].shift() <= dataframe['low']) | (dataframe['high'].shift() <= dataframe['close']))
        dataframe['buy_screener_condition_1'] = ( (dataframe['red_candle'].shift()) & (dataframe['low'].shift() > dataframe['sma10'].shift()))
        dataframe['buy_screener_condition_2'] = ( (dataframe['green_candle'].shift(2)) & (dataframe['green_candle'].shift(3)))
        
        # dataframe['tick_condition'] = ( (dataframe['low'].shift(-1) >= dataframe['high']))
        # dataframe['buy_screener_condition_1'] = ( (dataframe['red_candle']==True) & (dataframe['low'] > dataframe['sma10']))
        # dataframe['buy_screener_condition_2'] = ( (dataframe['green_candle'].shift()==True) & (dataframe['green_candle'].shift(2)==True))
        
        dataframe['buy_ohlc_condition'] = \
                            (
                                (dataframe['buy_screener_condition_1'] == True) &\
                                (dataframe['buy_screener_condition_2']==True) &\
                                (dataframe['tick_condition'])
                            )
        return dataframe


    def sell_ohlc_condition(self, dataframe):
        return True

    def buy_tick_condition(self):
        return True

    def sell_tick_condition(self):
        return True

