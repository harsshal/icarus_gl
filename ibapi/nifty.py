from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
from scipy.stats import linregress


import plotly.graph_objects as go
from plotly.subplots import make_subplots

matplotlib.use('tkAgg')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

def draw_candle_chart_v1(sample_df, peaks, troughs, region=None, cutoff=None):
    # Create figure and subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(15, 10), sharex=True, gridspec_kw={'height_ratios': [3, 1, 1]})


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
    ax1.bar(up.index, up.close - up.open, width, bottom=up.open, color=col1)
    ax1.bar(up.index, up.high - up.close, width2, bottom=up.close, color=col1)
    ax1.bar(up.index, up.low - up.open, width2, bottom=up.open, color=col1)

    # Plot down prices
    ax1.bar(down.index, down.close - down.open, width, bottom=down.open, color=col2)
    ax1.bar(down.index, down.high - down.open, width2, bottom=down.open, color=col2)
    ax1.bar(down.index, down.low - down.close, width2, bottom=down.close, color=col2)

    # Plot peaks and troughs only until cutoff
    if cutoff is not None:
        valid_peaks = [p for p in peaks if p <= cutoff]
        valid_troughs = [t for t in troughs if t <= cutoff]
    else:
        valid_peaks = peaks
        valid_troughs = troughs

    ax1.plot(valid_peaks, sample_df['close'][valid_peaks], "x", label='Peaks')
    ax1.plot(valid_troughs, sample_df['close'][valid_troughs], "o", label='Troughs')

    # Draw horizontal lines from each peak to the next
    for i in range(len(valid_peaks) - 1):
        ax1.hlines(sample_df['close'][valid_peaks[i]], xmin=valid_peaks[i], xmax=valid_peaks[i + 1], colors='blue')
    for i in range(len(valid_troughs) - 1):
        ax1.hlines(sample_df['close'][valid_troughs[i]], xmin=valid_troughs[i], xmax=valid_troughs[i + 1], colors='orange')

    # Plot SMAs
    ax1.plot(sample_df.index, sample_df['SMA_short'], label='SMA_short', color='blue')
    ax1.plot(sample_df.index, sample_df['SMA_long'], label='SMA_long', color='orange')

    # Rotate x-axis tick labels
    plt.xticks(rotation=45, ha='right')

    # Add legend
    ax1.set_ylabel('Price')
    ax1.legend()

    # Plot RSI
    ax2.plot(sample_df.index, sample_df['RSI'], label='RSI', color='purple')
    ax2.axhline(70, color='red', linestyle='--')
    ax2.axhline(30, color='green', linestyle='--')
    ax2.set_ylabel('RSI')
    ax2.legend()

    # Plot position
    ax3.plot(sample_df.index, sample_df['position'], label='Position', color='red')
    ax3.set_ylabel('Position')
    ax3.legend()

    # Display candlestick chart
    plt.show()

def draw_candle_chart(sample_df, peaks, troughs, region=None, cutoff=None):
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[3, 1, 1],
        subplot_titles=("Candlestick", "RSI", "Position"),
        vertical_spacing=0.1
    )

    # Candlestick chart
    fig.add_trace(go.Candlestick(x=sample_df.index,
                                 open=sample_df['open'],
                                 high=sample_df['high'],
                                 low=sample_df['low'],
                                 close=sample_df['close'],
                                 name='Candlestick'), row=1, col=1)

    # Plot peaks and troughs
    fig.add_trace(go.Scatter(x=sample_df.index[peaks], y=sample_df['close'][peaks],
                             mode='markers', name='Peaks',
                             marker=dict(color='red', size=10)), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=sample_df.index[troughs], y=sample_df['close'][troughs],
                             mode='markers', name='Troughs',
                             marker=dict(color='blue', size=10)), row=1, col=1)

    # Plot SMAs
    fig.add_trace(go.Scatter(x=sample_df.index, y=sample_df['SMA_short'],
                             mode='lines', name='SMA_short', line=dict(color='blue')), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=sample_df.index, y=sample_df['SMA_long'],
                             mode='lines', name='SMA_long', line=dict(color='orange')), row=1, col=1)

    # RSI subplot
    fig.add_trace(go.Scatter(x=sample_df.index, y=sample_df['RSI'],
                             mode='lines', name='RSI', line=dict(color='purple')), row=2, col=1)

    # Position subplot
    fig.add_trace(go.Scatter(x=sample_df.index, y=sample_df['position'],
                             mode='lines', name='Position', line=dict(color='red')), row=3, col=1)

    fig.update_layout(
        title='Candlestick Chart with SMA, RSI, and Position',
        hoversubplots='axis',
        hovermode='x unified',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Price'),
        yaxis2=dict(title='RSI'),
        yaxis3=dict(title='Position')
    )

    # remove rangeslider
    fig.update(layout_xaxis_rangeslider_visible=False)

    fig.show()

def find_sup_res(series, distance=20):
    peaks, _ = find_peaks(series, distance=distance)
    troughs, _ = find_peaks(-series, distance=distance)
    return peaks, troughs


def calculate_rsi(data, window=14):
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


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

        #self.reqHistoricalData(1, contract, '', '100 D', '1 day', 'MIDPOINT', 1, 1, False, [])
        #self.reqHistoricalData(1, contract, '', '10 D', '5 mins', 'MIDPOINT', 1, 1, False, [])
        self.reqHistoricalData(1, contract, '', '10 D', '5 mins', 'ADJUSTED_LAST', 1, 1, False, [])


    def historicalData(self, reqId, bar):
        self.data.append(bar)

    def historicalDataEnd(self, reqId, start, end):
        self.historical_data_end = True
        self.calculate_indicators()

    def calculate_indicators(self):
        # Extract attributes from the first element of self.data
        attributes = vars(self.data[0]).keys()

        # Create a DataFrame using the extracted attributes
        df = pd.DataFrame([{attr: getattr(bar, attr) for attr in attributes} for bar in self.data])

        df['date'] = pd.to_datetime(df['date'])

        df['actual'] = df['close'].rolling(window=1).mean()
        df['SMA_short'] = df['close'].rolling(window=21, min_periods=1).mean()
        df['SMA_long'] = df['close'].rolling(window=34, min_periods=1).mean()

        df['signal'] = 0
        df['signal'] = np.where(df['SMA_short'] > df['SMA_long'] * 1.1, 1, 0)

        df['RSI'] = calculate_rsi(df)

        # Identify the first candle of each trading day
        df['first_candle'] = (df['date'].dt.date != df['date'].shift(1).dt.date).astype(int).cumsum()

        df['position'] = np.nan  # Initialize positions to 0

        for day in df['first_candle'].unique():
            day_df = df[df['first_candle'] == day]
            position_opened = False  # Reset for each day
            position_closed = False  # Reset for each day

            if len(day_df) > 0:
                first_candle_range = day_df.iloc[0]['high'] - day_df.iloc[0]['low']
                for idx in day_df.index:
                    if not position_opened and day_df.at[idx, 'close'] > day_df.iloc[0]['high']:
                        df.at[idx, 'position'] = 1  # Open long position
                        position_opened = True
                        #print(f"Opened long position at index {idx}")
                    elif not position_opened and day_df.at[idx, 'close'] < day_df.iloc[0]['low']:
                        df.at[idx, 'position'] = -1  # Open short position
                        position_opened = True
                        #print(f"Opened short position at index {idx}")
                    if position_opened:
                        break  # Exit loop after opening a position

                # Close position based on the slope of the last 4 candle midpoints
                if len(day_df) >= 4 and position_opened:
                    for idx in day_df.index[5:]:  # Start checking after the first 3 candles
                        recent_window = day_df.loc[:idx, 'average'].tail(4).reset_index()
                        slope, intercept, r_value, p_value, std_err = linregress(recent_window.index, recent_window['average'])
                        #print(idx, position_opened, position_closed, slope)
                        
                        if abs(slope) < 0.01 or \
                            (day_df.at[idx, 'close'] > day_df.iloc[0]['high'] and slope < 0) or \
                            (day_df.at[idx, 'close'] < day_df.iloc[0]['low'] and slope > 0):  # You can adjust the threshold for the slope
                            df.at[idx, 'position'] = 0  # Close position
                            #print(f"Closed position at index {idx}")
                            break  # Exit loop after closing a position

            # # Forward fill the position for the rest of the day if the position is opened and not closed
            # if position_opened and not position_closed:
            #     df.loc[day_df.index, 'position'] = df.loc[day_df.index[0], 'position']

        df['position'] = df['position'].ffill().fillna(0)
        df['signal'] = df['position'].diff()

        self.df = df
        self.execute_trades(df)


    def execute_trades(self, df):
        contract = Contract()
        contract.symbol = 'AAPL'
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'

        for i in range(len(df)):
            if df['signal'].iloc[i] == 1:
                order = Order()
                order.action = 'BUY'
                order.orderType = 'MKT'
                order.totalQuantity = 100
                order.eTradeOnly = False
                order.firmQuoteOnly = False
                
                self.placeOrder(self.nextOrderId, contract, order)
                self.nextOrderId += 1
            elif df['signal'].iloc[i] == -1:
                order = Order()
                order.action = 'SELL'
                order.orderType = 'MKT'
                order.totalQuantity = 100
                order.eTradeOnly = False
                order.firmQuoteOnly = False
                
                self.placeOrder(self.nextOrderId, contract, order)
                self.nextOrderId += 1

        self.disconnect()


def main():
    app = IBApi()
    app.connect('127.0.0.1', 7497, 0)
    app.run()

    sample_df = app.df

    # Determine cutoff point as the length of the dataframe minus some buffer, e.g., last 10 values
    cutoff = len(sample_df) - 10

    peaks, troughs = find_sup_res(sample_df['close'],20)
    draw_candle_chart(sample_df, peaks, troughs, region=0.0001, cutoff=cutoff)

    #print(sample_df)
    # calculate PNL as position * difference in price
    #print("PNL: ", (((sample_df['close'] - sample_df['close'].shift(1)))*sample_df['position']).cumsum())



if __name__ == "__main__":
    main()
