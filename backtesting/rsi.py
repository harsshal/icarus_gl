import numpy as np
import pandas as pd
from backtesting import Strategy, Backtest
from backtesting.test import SMA

import sys
import os

def add_to_sys_path(path_str):
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), path_str))
    sys.path.insert(0, parent_dir)

add_to_sys_path('../ibapi')

from ibkr_data import get_ibkr_data

def rsi(close_prices, period=14):
    """Calculate RSI using NumPy arrays to ensure compatibility with the backtesting framework."""
    close_diff = np.diff(close_prices)  
    gain = np.where(close_diff > 0, close_diff, 0)
    loss = np.where(close_diff < 0, -close_diff, 0)

    avg_gain = np.zeros_like(close_prices)
    avg_loss = np.zeros_like(close_prices)

    avg_gain[period] = np.mean(gain[:period])
    avg_loss[period] = np.mean(loss[:period])

    for i in range(period + 1, len(close_prices)):
        avg_gain[i] = (avg_gain[i-1] * (period - 1) + gain[i-1]) / period
        avg_loss[i] = (avg_loss[i-1] * (period - 1) + loss[i-1]) / period

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    rsi[:period] = 50  
    return rsi

class RSI_Strategy(Strategy):
    rsi_period = 14
    overbought = 70
    oversold = 30

    def init(self):
        """Initialize RSI indicator"""
        self.rsi = self.I(rsi, self.data.Close, self.rsi_period)

    def next(self):
        """Define entry/exit logic based on RSI"""
        if self.rsi[-1] < self.oversold:
            self.buy()

        elif self.rsi[-1] > self.overbought:
            self.sell()

aapl = get_ibkr_data('AAPL', '', '1 D', '1 min')

bt = Backtest(aapl, RSI_Strategy, cash=10000, commission=0.0001)
print(bt.run())
bt.plot()

