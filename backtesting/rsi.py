import pandas as pd
from backtesting import Strategy, Backtest
from ibkr_data import get_ibkr_data

def RSI(series, period):
    series = pd.Series(series)
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

class ImprovedRSIStrategy(Strategy):
    rsi_period = 14
    overbought = 70
    oversold = 30
    stop_loss = 0.02
    take_profit = 0.04

    def init(self):
        self.rsi = self.I(RSI, self.data.Close, self.rsi_period)

    def next(self):
        if not self.position:
            if self.rsi[-1] < self.oversold:
                self.buy(size=0.2)

        elif self.position.is_long:
            entry_price = self.trades[-1].entry_price if self.trades else None

            if entry_price:
                if self.data.Close[-1] < entry_price * (1 - self.stop_loss):
                    self.position.close()
                elif self.data.Close[-1] > entry_price * (1 + self.take_profit):
                    self.position.close()

aapl = get_ibkr_data(
    ticker='AAPL',
    endDateTime='20241016 00:00:00 US/Eastern',
    durationStr='30 D',
    barSizeSetting='1 hour',
    primaryExchange="SMART"
)

if aapl.empty:
    print("No data received for ticker: AAPL")
else:
    bt = Backtest(aapl, ImprovedRSIStrategy, cash=10000, commission=0.0001)
    stats = bt.run()
    print(stats)
    bt.plot()
