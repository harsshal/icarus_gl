from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from threading import Thread
import pandas as pd
#from sqlalchemy import create_engine
#from dotenv import load_dotenv
import os
import sys
import time

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backtesting.py'))
sys.path.insert(0, parent_dir)

from ibapi import ibkr_data

def get_tickers_from_sql(db_url, table_name):
    """
    Read tickers from an SQL table.

    Parameters:
    - db_url: the database connection URL (e.g., mysql+pymysql://user:password@localhost/dbname)
    - table_name: the name of the table to read from

    Returns:
    A list of tickers.
    """
    engine = create_engine(db_url)
    query = f"SELECT ticker FROM {table_name}"
    df = pd.read_sql(query, engine)
    return df['ticker'].tolist()  # Convert the 'ticker' column to a list


def fetch_historical_data_for_sp500(tickers, date, history_period, bar_size):
    """
    Fetch historical data for a list of tickers using the IBKR API.
    
    Parameters:
    - tickers: list of ticker symbols.
    - end_date: end date for historical data (format: 'YYYYMMDD HH:MM:SS').
    - history_period: period of historical data to request (e.g., '1 D', '1 M').
    - bar_size: bar size (e.g., '1 min', '5 min', '1 day').

    Returns:
    A combined DataFrame of historical data for all tickers.
    """
    # Create an empty list to store individual DataFrames
    all_data = []

    for ticker in tickers:
        print(f"Fetching historical data for {ticker}")
        try:
            df = get_ibkr_data(ticker, date, history_period, bar_size)
            df['Ticker'] = ticker  # Add a column for the ticker
            all_data.append(df)
        except Exception as e:
            print(f"Failed to fetch data for {ticker}: {e}")
        time.sleep(1)  

    # Combine all individual DataFrames into one
    if all_data:
        combined_df = pd.concat(all_data)
        return combined_df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no data


def main():
    load_dotenv()

    db_url = os.getenv('db_url')
    table_name = 'sp500_tickers'

    # Fetch tickers from SQL table
    #tickers = get_tickers_from_sql(db_url, table_name)
    #print(f"Tickers fetched from SQL: {tickers}")  # Debugging print

    # Fetch historical data for all tickers
    tickers = ('AAPL','AOS','ABT','ABBV')
    date = '20240925 23:59:59'  
    history_period = '1 D'  
    bar_size = '5 mins'  

    historical_data_df = fetch_historical_data_for_sp500(tickers, date, history_period, bar_size)

    # Print the DataFrame
    print(historical_data_df)

    # Optionally, save the combined data to a CSV or a new SQL table
    # historical_data_df.to_csv('historical_data.csv', index=False)

    # Or save to SQL table:
    # engine = create_engine(db_url)
    # historical_data_df.to_sql('historical_data_sp500', con=engine, if_exists='replace', index=False)


if __name__ == "__main__":
    main()
