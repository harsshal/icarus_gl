from sklearn.linear_model import LinearRegression
import numpy as np

def mean_reversion_price(trade_data):
    return sum(trade_data) / len(trade_data)

def momentum_price(trade_data):
    # using linear regression

    X = np.array(range(len(trade_data))).reshape(-1, 1)
    y = trade_data
    model = LinearRegression().fit(X, y)
    return model.predict([[len(trade_data)]])

def sma(trade_data,  window = 20):
    sma = trade_data.rolling(window=window).mean()
    return sma

def bollinger(trade_data, window=20, num_std=2):
    rolling_mean = trade_data.rolling(window=window).mean()
    rolling_std = trade_data.rolling(window=window).std()
    
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    
    return [upper_band.tolist(), lower_band.tolist()]

def macd(trade_data, short_window=12, long_window=26, signal_window=9):
    short_ema = trade_data.ewm(span=short_window, adjust=False).mean()
    long_ema = trade_data.ewm(span=long_window, adjust=False).mean()
    macd_line = short_ema - long_ema

    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    macd_histogram = macd_line - signal_line
    
    return [macd_line.tolist(), signal_line.tolist(), macd_histogram.tolist()]


def rsi(trade_data, window=14):
    delta = trade_data.diff()
    
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def vwap(price_data, volume_data):
    cum_price_volume = (price_data * volume_data).cumsum()
    cum_volume = volume_data.cumsum()

    vwap = cum_price_volume / cum_volume
    return vwap

def mfi(high, low, close, volume, window=14):
    typical_price = (high + low + close) / 3
    raw_money_flow = typical_price * volume

    positive_flow = raw_money_flow.where(typical_price > typical_price.shift(1), 0)
    negative_flow = raw_money_flow.where(typical_price < typical_price.shift(1), 0)
    
    positive_flow_sum = positive_flow.rolling(window=window).sum()
    negative_flow_sum = negative_flow.rolling(window=window).sum()   
    money_flow_ratio = positive_flow_sum / negative_flow_sum

    mfi = 100 - (100 / (1 + money_flow_ratio))
    
    return mfi