# https://colab.research.google.com/drive/1qMvE5j97_w79SGyfNY8j4-xlhbnM63qV#scrollTo=47QRF-5ucGqY

import pandas as pd
import pandas_ta as ta
from backtesting import Strategy, Backtest

from ibkr_data import get_ibkr_data
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


df = get_ibkr_data(ticker='AAPL', end_date='20240631 00:00:00 US/Eastern', 
                     history_period='1 D', bar_size='1 min')

backcandles = 2

df["EMA"]=ta.ema(df.Close, length=2)
df["ATR"] = ta.atr(df.High, df.Low, df.Close, length=14)


my_bbands = ta.bbands(df.Close, length=200, std=4)
df=df.join(my_bbands)

my_bbands = ta.bbands(df.Close, length=200, std=0.5)
df=df.join(my_bbands)

df['BBUP_EMA'] = df['EMA'] + 4 * df['EMA'].rolling(200).std()
df['BBUP_Close'] = df['EMA'] + 4 * df['Close'].rolling(200).std()
df['BBUP_MidPrice'] = df['EMA'] + 4 * ((df['Close']+df['Open']+df['High'])/3).rolling(200).std()

df['BBDN'] = df['EMA'] - 0.5 * df['Close'].rolling(200).std()
df.loc[(df['Close'] < df['BBDN']), 'EXIT'] = 1

# Initialize the 'Signal' column with default values (0)
df['EMASignal'] = 0

# Iterate over the DataFrame rows starting from the index equal to 'backcandles'
for i in range(backcandles, len(df)):
    # Extract the relevant data for the current and previous candles
    previous_closes = df.iloc[i-backcandles:i+1]['Close'].values # i+1 to include current candle (no lookahead)
    ema_values = df.iloc[i-backcandles:i+1]['EMA'].values # i+1 to include current candle (no lookahead)

    print(i, previous_closes, ema_values)
    # Check if all previous closes are above the corresponding EMA values
    if all(close > ema for close, ema in zip(previous_closes, ema_values)):
        df['EMASignal'].iloc[i] = 2

df['TotalSignal'] = df.apply(lambda row: 2 if row['EMASignal'] == 2 and row['Close'] < row['BBUP_EMA'] else 0, axis=1)

print(df['TotalSignal'].value_counts())
print(df.tail())


dfopt = df[0:].copy()
# dfopt["Date"] = pd.to_datetime(dfopt["Date"])
# dfopt.set_index(["Date"], inplace=True)

def SIGNAL():
    return dfopt.TotalSignal

class MyStrat(Strategy):
    mysize = 0.1
    trailperc = 0.02
    
    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)
        

    def next(self):
        super().next()
        
        sltr = self.data.Close[-1]*self.trailperc

        for trade in self.trades: 
            if trade.is_long: 
                trade.sl = max(trade.sl or -np.inf, self.data.Close[-1] - sltr)
            else:
                trade.sl = min(trade.sl or np.inf, self.data.Close[-1] + sltr) 
     
        if self.signal1==2 and len(self.trades)==0:
            self.buy(sl=sltr, size=self.mysize)
        
bt = Backtest(dfopt, MyStrat, cash=100000, margin=1/5, commission=0.05)
stats, heatmap = bt.optimize(trailperc=[i/100 for i in range(1, 20)],
                    maximize='Return [%]', max_tries=300,
                        random_state=0,
                        return_heatmap=True)
print(stats)