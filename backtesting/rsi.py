import pandas as pd
from backtesting import Strategy, Backtest
from ibkr_data import get_ibkr_data

def RSI(series, period):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

class RSIStrategy(Strategy):
    rsi_period = 14
    overbought = 70
    oversold = 30
    trade_count = 0

    def init(self):
        self.rsi = self.I(RSI, self.data.Close, self.rsi_period)

    def next(self):
        if self.trade_count >= 5:
            return

        if self.rsi[-1] < self.oversold and not self.position:
            self.buy()
            self.trade_count += 1
            print(f"Buy at {self.data.Close[-1]} on {self.data.index[-1]}")

        elif self.rsi[-1] > self.overbought and self.position:
            self.position.close()
            self.trade_count += 1
            print(f"Sell at {self.data.Close[-1]} on {self.data.index[-1]}")

data = get_ibkr_data(
    ticker='F',
    endDateTime='20241016 00:00:00 US/Eastern',
    durationStr='1 D',
    barSizeSetting='1 min'
)

if not data.empty:
    bt = Backtest(data, RSIStrategy, cash=10000, commission=0.0001)
    stats = bt.run()
    print(stats)
    bt.plot()
