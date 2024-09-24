# first 5 minute candle high / low break
# starting 5 mins and ending 5 mins
# first candle which broke first 5 min high / low
# support / resistance at different intervals
#central pivot range
# 1D, 1W 1 month and RSI

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import pandas as pd
import numpy as np
from scipy.signal import find_peaks

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'include'))
import plotting
import sup_res

from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('tkAgg')


def draw_candle_chart_v1(sample_df, region=None):
    # Create figure
    f = plt.figure(figsize=(15, 10))

    # Define width of candlestick elements
    width = 0.4
    width2 = 0.05

    print(sample_df)

    # Define up and down prices
    up = sample_df[sample_df.close >= sample_df.open]
    down = sample_df[sample_df.close < sample_df.open]

    # Define colors to use
    col1 = 'green'
    col2 = 'red'

    # Plot up prices
    plt.bar(up.index, up.close - up.open, width, bottom=up.open, color=col1)
    plt.bar(up.index, up.high - up.close, width2, bottom=up.close, color=col1)
    plt.bar(up.index, up.low - up.open, width2, bottom=up.open, color=col1)

    # Plot down prices
    plt.bar(down.index, down.close - down.open, width, bottom=down.open, color=col2)
    plt.bar(down.index, down.high - down.open, width2, bottom=down.open, color=col2)
    plt.bar(down.index, down.low - down.close, width2, bottom=down.close, color=col2)

    # Plot support and resistance
    if 'support' in sample_df.columns:
        plt.plot(sample_df.index, sample_df['support'], color='blue', label='Support')
    if 'resistance' in sample_df.columns:
        plt.plot(sample_df.index, sample_df['resistance'], color='orange', label='Resistance')


    # Rotate x-axis tick labels
    plt.xticks(rotation=45, ha='right')

    # Add legend
    #plt.legend()

    # Display candlestick chart
    plt.show()


def draw_candle_chart(sample_df, peaks, troughs, region=None, cutoff=None):
    # Create figure
    f = plt.figure(figsize=(15, 10))

    # Define width of candlestick elements
    width = 0.4
    width2 = 0.05

    # Define up and down prices
    up = sample_df[sample_df.close >= sample_df.open]
    down = sample_df[sample_df.close < sample_df.open]

    # Define colors to use
    col1 = 'green'
    col2 = 'red'

    # Plot up prices
    plt.bar(up.index, up.close - up.open, width, bottom=up.open, color=col1)
    plt.bar(up.index, up.high - up.close, width2, bottom=up.close, color=col1)
    plt.bar(up.index, up.low - up.open, width2, bottom=up.open, color=col1)

    # Plot down prices
    plt.bar(down.index, down.close - down.open, width, bottom=down.open, color=col2)
    plt.bar(down.index, down.high - down.open, width2, bottom=down.open, color=col2)
    plt.bar(down.index, down.low - down.close, width2, bottom=down.close, color=col2)

    # Plot peaks and troughs only until cutoff
    if cutoff is not None:
        valid_peaks = [p for p in peaks if p <= cutoff]
        valid_troughs = [t for t in troughs if t <= cutoff]
    else:
        valid_peaks = peaks
        valid_troughs = troughs

    plt.plot(valid_peaks, sample_df['close'][valid_peaks], "x", label='Peaks')
    plt.plot(valid_troughs, sample_df['close'][valid_troughs], "o", label='Troughs')

    # Plot SMAs
    plt.plot(sample_df.index, sample_df['SMA_short'], label='SMA_short', color='blue')
    plt.plot(sample_df.index, sample_df['SMA_long'], label='SMA_long', color='orange')

    # Rotate x-axis tick labels
    plt.xticks(rotation=45, ha='right')

    if region is not None:
        for x in valid_peaks:
            plt.hlines(sample_df['close'][x], xmin=sample_df.index[0], xmax=sample_df.index[-1], colors='blue')
            plt.fill_between(sample_df.index, sample_df['close'][x] - sample_df['close'][x] * region,
                             sample_df['close'][x] + sample_df['close'][x] * region, alpha=0.4)

    # Add legend
    plt.legend()

    # Display candlestick chart
    plt.show()



def find_sup_res_v1(sample_df, window=5):
    # Calculate rolling high of highs and low of lows
    sample_df['resistance'] = sample_df['high'].rolling(window=window).max().bfill()
    sample_df['support'] = sample_df['low'].rolling(window=window).min().bfill()

    return sample_df

def find_sup_res_v2(sample_df, window=10):
    # Calculate rolling high of highs and low of lows
    sample_df['rolling_high'] = sample_df['high'].rolling(window=window).max().bfill()
    sample_df['rolling_low'] = sample_df['low'].rolling(window=window).min().bfill()

    # Identify support and resistance levels
    resistance_indices, _ = find_peaks(sample_df['rolling_high'].dropna(), width=5)
    support_indices, _ = find_peaks(-sample_df['rolling_low'].dropna(), width=5)

    print(resistance_indices, support_indices)

    sample_df['resistance'] = np.nan
    sample_df['support'] = np.nan

    sample_df.loc[sample_df.index[resistance_indices], 'resistance'] = sample_df['rolling_high'].iloc[resistance_indices]
    sample_df.loc[sample_df.index[support_indices], 'support'] = sample_df['rolling_low'].iloc[support_indices]

    sample_df.fillna(method='ffill').fillna(method='bfill')

    return sample_df

def find_sup_res(series):
    peaks, _ = find_peaks(series)
    troughs, _ = find_peaks(-series)
    return peaks, troughs


class IBApi(EWrapper, EClient):
    df = pd.DataFrame()

    def __init__(self):
        EClient.__init__(self, self)
        self.data = []
        self.nextOrderId = None
        self.historical_data_end = False

    def nextValidId(self, orderId):
        self.nextOrderId = orderId
        self.start()

    def start(self):
        contract = Contract()
        contract.symbol = 'AAPL'
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'

        # Request historical data
        #self.reqHistoricalData(1, contract, '', '100 D', '5 mins', 'MIDPOINT', 1, 1, False, [])
        self.reqHistoricalData(1, contract, '', '100 D', '1 day', 'MIDPOINT', 1, 1, False, [])

    def historicalData(self, reqId, bar):
        self.data.append(bar)

    def historicalDataEnd(self, reqId, start, end):
        self.historical_data_end = True
        self.calculate_indicators()

    def calculate_indicators(self):
        #df = pd.DataFrame(self.data)
        df = pd.DataFrame(list(map(lambda x:[x.open,x.high,x.low,x.close,x.date],self.data))
                          ,columns=["open","high","low","close","date"])
        df['date'] = pd.to_datetime(df['date'])

        df['actual'] = df['close'].rolling(window=1).mean()
        df['SMA_short'] = df['close'].rolling(window=21, min_periods=1).mean()
        df['SMA_long'] = df['close'].rolling(window=34, min_periods=1).mean()

        df['signal'] = 0
        df['signal'] = np.where(df['actual'] > df['SMA_long'], 1, 0)
        df['signal'] = np.where(df['actual'] < df['SMA_short'], -1, 0)
        #df['signal'][10:] = np.where(df['SMA_short'][10:] > df['SMA_long'][10:], 1, 0)
        #df['position'] = df['signal'].diff()

        print(df)
        print(sum((df['signal'] * df['close']).dropna()))

        self.df = df

        self.execute_trades(df)

    def execute_trades(self, df):
        contract = Contract()
        contract.symbol = 'AAPL'
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'

        for i in range(len(df)):
            if df['signal'].iloc[i] == 1 :
                #print(f"Buy signal on {df['date'].iloc[i]}: {df['close'].iloc[i]}")
                order = Order()
                order.action = 'BUY'
                order.orderType = 'MKT'
                order.totalQuantity = 100
                order.eTradeOnly = False
                order.firmQuoteOnly = False
                #self.placeOrder(self.nextOrderId, contract, order)
                self.nextOrderId += 1
            elif df['signal'].iloc[i] == -1:
                #print(f"Sell signal on {df['date'].iloc[i]}: {df['close'].iloc[i]}")
                order = Order()
                order.action = 'SELL'
                order.orderType = 'MKT'
                order.totalQuantity = 100
                order.eTradeOnly = False
                order.firmQuoteOnly = False
                #self.placeOrder(self.nextOrderId, contract, order)
                self.nextOrderId += 1

        self.disconnect()

def main():
    app = IBApi()
    app.connect('127.0.0.1', 7497, 0)
    app.run()

    sample_df = app.df
    peaks, troughs = find_sup_res(sample_df['close'])
    draw_candle_chart(sample_df, peaks, troughs, region=0.0001)

if __name__ == "__main__":
    main()

