# first 5 minute candle high / low break
# starting 5 mins and ending 5 mins
# first candle which broke first 5 min high / low

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import pandas as pd
import numpy as np

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'include'))
import plotting
import sup_res


from sklearn.neighbors import KernelDensity
from scipy.signal import argrelextrema
import numpy as np
from scipy.signal import find_peaks
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('tkAgg')


def draw_candle_chart(sample_df, peaks, region=None):
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

    # Rotate x-axis tick labels
    plt.xticks(rotation=45, ha='right')

    if region is not None:
        for x in peaks:
            plt.hlines(x, xmin=sample_df.index[0], xmax=sample_df.index[-1])
            plt.fill_between(sample_df.index, x - x * region, x + x * region, alpha=0.4)

    # Display candlestick chart
    plt.show()


def find_price_peaks(sample):
    maxima = argrelextrema(sample.values, np.greater)[0]
    minima = argrelextrema(sample.values, np.less)[0]

    extrema = np.concatenate((maxima, minima))
    extrema_prices = sample.iloc[extrema].values.reshape(-1, 1)
    initial_price = extrema_prices[0][0]
    print("Initial price:", initial_price, extrema_prices)

    kde = KernelDensity(kernel='gaussian', bandwidth=initial_price/300).fit(extrema_prices)

    a, b = min(extrema_prices), max(extrema_prices)
    price_range = np.linspace(a, b, 1000).reshape(-1, 1)
    pdf = np.exp(kde.score_samples(price_range))

    peaks = find_peaks(pdf, prominence=0.01)[0]

    return price_range[peaks].flatten()

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

        df['actual'] = df['close'].rolling(window=1).mean()
        df['SMA_short'] = df['close'].rolling(window=21).mean()
        df['SMA_long'] = df['close'].rolling(window=34).mean()

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
    peaks = find_price_peaks(sample_df['close'])
    draw_candle_chart(sample_df, peaks, region=0.0001)

if __name__ == "__main__":
    main()

