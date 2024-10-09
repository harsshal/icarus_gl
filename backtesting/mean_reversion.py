import pandas as pd
from backtesting import Strategy, Backtest
from backtesting.test import SMA
from ibkr_data import get_ibkr_data

def std_3(arr, n):
    return pd.Series(arr).rolling(n).std() * 2

class MeanReversion(Strategy):
    roll = 50

    def init(self):
        self.he = self.data.Close

        self.he_mean = self.I(SMA, self.he, self.roll)
        self.he_std = self.I(std_3, self.he, self.roll)
        self.he_upper = self.he_mean + self.he_std
        self.he_lower = self.he_mean - self.he_std

        self.he_close = self.I(SMA, self.he, 1)
        self.count = 0

    def next(self):
        
        #print("Iteration:: ", self.count, self.he[self.count],self.he_close[-1], self.he_mean[-1], self.he_lower[-1], self.he_upper[-1])
        self.count += 1

        if self.he_close < self.he_lower:
            self.buy(
                sl = self.he_close * 0.95,
                tp = self.he_lower * 1.05,
            )

        if self.he_close > self.he_upper:
            self.sell(
                sl = self.he_close * 1.05,
                tp = self.he_upper * 0.95,
            )

aapl = get_ibkr_data(ticker='AAPL', end_date='20240631 00:00:00 US/Eastern', 
                     history_period='10 D', bar_size='1 min')
bt = Backtest(aapl, MeanReversion, cash=10000, commission=0.0001)
print(bt.run())
bt.plot()