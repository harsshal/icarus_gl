#!/usr/bin/env python3


from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from threading import Thread
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()
from save_sql import save_dataframe_to_mysql  
import os
import argparse
import time

from ibkr_data import get_ibkr_data
from datetime import datetime

def get_tickers_from_sql(db_url, table_name='instruments', ticker=None):
    engine = create_engine(db_url)
    
    # If a specific ticker is provided, fetch only that ticker
    if ticker:
        query = f"SELECT id, symbol FROM {table_name} WHERE symbol = '{ticker}'"
    else:
        query = f"SELECT id, symbol FROM {table_name}"

    df = pd.read_sql(query, engine)

    # Create a dictionary mapping symbols to ids
    symbol_id_dict = dict(zip(df['symbol'], df['id']))

    return symbol_id_dict

def process_historical_data(df, ticker, instrument_id):
    if isinstance(df, pd.DataFrame) and not df.empty:
        # Reset the index to move the DateTime index to a column
        df = df.reset_index()

        # Convert 'Date' to datetime and split into 'Date' and 'Time'
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date  # Ensure 'Date' is a datetime.date
        df['Time'] = pd.to_datetime(df['Date'], errors='coerce').dt.time  # Ensure 'Time' is a datetime.time

        # Add UpdateTime as the current timestamp
        df['UpdateTime'] = pd.Timestamp.now()

        # Add InstrumentId as the id from the instruments table
        df['InstrumentId'] = instrument_id

        # Remove the Ticker column if it exists (since you don't want it in the final result)
        df = df.drop(columns=['Ticker'], errors='ignore')

    else:
        print(f"No data to process for ticker {ticker}")
    
    return df

def fetch_historical_data_for_sp500(tickers_dict, date, history_period, bar_size):
    all_data = []

    for ticker, instrument_id in tickers_dict.items():
        print(f"Fetching historical data for {ticker}")
        try:
            df = get_ibkr_data(ticker, date, history_period, bar_size)

            # Ensure that only valid DataFrames are processed
            if isinstance(df, pd.DataFrame):
                # Process the DataFrame: split date, remove ticker, add instrument id
                df = process_historical_data(df, ticker, instrument_id)
                all_data.append(df)
            else:
                print(f"Invalid data type received for {ticker}: {type(df)}")
        except Exception as e:
            print(f"Failed to fetch data for {ticker}: {e}")
        time.sleep(5)  # Adjust the sleep time if needed

    # Combine all individual DataFrames into one
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        return combined_df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=str, default=None, required=True, help="Specify the date in format YYYYMMDD")
    parser.add_argument('--ticker', type=str, default=None, help="Specify the ticker symbol")

    args = parser.parse_args()
    load_dotenv()

    db_url = os.getenv('db_url')
    table_name = 'instruments'

    # Fetch the tickers, filter by specific ticker if provided
    tickers_dict = get_tickers_from_sql(db_url, table_name, ticker=args.ticker)
    print(f"Tickers fetched from SQL: {tickers_dict}")  

    # Dynamically get today's date and time in the format required by IBKR
    date_str = datetime.strptime(args.date, '%Y%m%d')
    date_obj = date_str.strftime('%Y%m%d %H:%M:%S')
    history_period = '1 D'  # Historical period to fetch
    bar_size = '1 min'  # Bar size

    # Fetch historical data using the date and ticker
    historical_data_df = fetch_historical_data_for_sp500(tickers_dict, date_obj, history_period, bar_size)

    # Ensure the final DataFrame has the necessary columns
    historical_data_df = historical_data_df[['InstrumentId', 'Date', 'Time', 'UpdateTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Barcount', 'Average']]

    # Print the DataFrame
    print(historical_data_df.head())
    print(historical_data_df.columns)

    # Specify the table name where data should be saved
    save_table = 'historical_prices'
    keys = ['InstrumentId', 'Date', 'Time']
    print(historical_data_df.dtypes)

    # Call the save function to save the DataFrame to MySQL
    save_dataframe_to_mysql(historical_data_df, db_url, save_table, primary_keys=keys)

if __name__ == "__main__":
    main()
