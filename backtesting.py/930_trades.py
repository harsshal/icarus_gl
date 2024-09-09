import pandas as pd
from ibkr_data import get_ibkr_data
from ibkr_order import IBOrderManager
from ibkr_scanner import get_ibkr_scanner

def trading_strategy(ticker, end_date, history_period, bar_size):
    # Fetch 5-minute historical data
    df = get_ibkr_data(ticker, end_date, history_period, bar_size)

    # Ensure we have data
    if df.empty:
        print(f"No historical data found for {ticker}.")
        return

    # Filter for the 9:30 AM candle
    df['time'] = df.index.time
    df_930 = df[df.index.time == pd.to_datetime('09:30').time()]
    
    if df_930.empty:
        print(f"No 9:30 AM data found for {ticker}.")
        return
    
    # Get the close price of the 9:30 AM candle
    close_930 = df_930.iloc[0]['Close']

    # Get the first 5-minute candle after 9:30 AM
    df_after_930 = df[df.index.time > pd.to_datetime('09:30').time()]
    
    if df_after_930.empty:
        print(f"No candles after 9:30 AM found for {ticker}.")
        return
    
    first_candle_after_930 = df_after_930.iloc[0]

    # Compare the close prices
    if first_candle_after_930['Close'] > close_930:
        print(f"Buying {ticker} since the first candle {first_candle_after_930['Close']} closed above the 9:30 candle {close_930}.")
        # Place a buy order with a trailing stop of 95%
        entry_price = first_candle_after_930['Close']
        trailing_stop_price = entry_price * 0.95  # 95% trailing stop
        order_manager = IBOrderManager(ticker, 'BUY', 'LMT', entry_price, 100)
        order_manager.send_order()

    elif first_candle_after_930['Close'] < close_930:
        print(f"Selling {ticker} since the first candle {first_candle_after_930['Close']} closed below the 9:30 candle {close_930}.")
        # Place a sell order with a trailing stop of 95%
        entry_price = first_candle_after_930['Close']
        trailing_stop_price = entry_price * 0.95  # 95% trailing stop
        order_manager = IBOrderManager(ticker, 'SELL', 'LMT', entry_price, 100)
        order_manager.send_order()

# TODO: orders not getting placed in ibkr
# TODO: need to use realtime data for paper trading

def main():
    # Fetch the top 50 gainers using the scanner
    df_scanner = get_ibkr_scanner()

    if df_scanner.empty:
        print("No stocks found from the scanner.")
        return

    # Loop through the top 50 stocks provided by the scanner
    for _, row in df_scanner[:5].iterrows():
        ticker = row['contract']
        print(f"Running strategy for {ticker}")
        # Apply the strategy to each stock
        trading_strategy(ticker, '20240909 00:00:00', '1 D', '5 mins')

if __name__ == "__main__":
    main()
