from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from threading import Thread
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from save_sql import save_dataframe_to_mysql  
import hputils
import os
import time

from ibkr_data import get_ibkr_data


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
    return df['ticker'].tolist() 


def process_historical_data(df, ticker, ticker_index):
    """
    Process the historical data DataFrame by splitting the Date index into Date and Timestamp, 
    removing the Ticker column, and adding a Ticker Index column.
    
    Parameters:
    - df: DataFrame containing the historical data
    - ticker: ticker symbol for the current stock
    - ticker_index: the index of the ticker in the SQL table
    
    Returns:
    - Processed DataFrame
    """
    if isinstance(df, pd.DataFrame) and not df.empty:
        # Reset the index to move the DateTime index to a column
        df = df.reset_index()

        # Split the index column (which is now 'Date') into 'Date' and 'Timestamp'
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Timestamp'] = df['Date'].dt.time  # Extract just the time
        df['Date'] = df['Date'].dt.date  # Extract just the date

        # Add the ticker's index from the SQL table
        df['Ticker Index'] = ticker_index  # Use the ticker's index from the SQL table

        # Remove the Ticker column if it exists (since you don't want it in the final result)
        df = df.drop(columns=['Ticker'], errors='ignore')

    else:
        print(f"No data to process for ticker {ticker}")
    
    return df


def fetch_historical_data_for_sp500(tickers, date, history_period, bar_size, ticker_indices):
    """
    Fetch historical data for a list of tickers using the IBKR API.
    
    Parameters:
    - tickers: list of ticker symbols.
    - end_date: end date for historical data (format: 'YYYYMMDD HH:MM:SS').
    - history_period: period of historical data to request (e.g., '1 D', '1 M').
    - bar_size: bar size (e.g., '1 min', '5 min', '1 day').
    - ticker_indices: a dictionary that maps tickers to their index in the SQL table.

    Returns:
    A combined DataFrame of historical data for all tickers.
    """
    all_data = []

    for ticker in tickers:
        print(f"Fetching historical data for {ticker}")
        try:
            df = get_ibkr_data(ticker, date, history_period, bar_size)

            # Ensure that only valid DataFrames are processed
            if isinstance(df, pd.DataFrame):
                # Process the DataFrame: split date, remove ticker, add index
                ticker_index = ticker_indices[ticker]
                df = process_historical_data(df, ticker, ticker_index)

                all_data.append(df)
            else:
                print(f"Invalid data type received for {ticker}: {type(df)}")
        except Exception as e:
            print(f"Failed to fetch data for {ticker}: {e}")
        time.sleep(2)  

    # Combine all individual DataFrames into one
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        return combined_df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no data


def main():
    load_dotenv()

    db_url = os.getenv('db_url')
    table_name = 'sp500_tickers'

    # Fetch tickers from SQL table
    tickers = get_tickers_from_sql(db_url, table_name)
    print(f"Tickers fetched from SQL: {tickers}")  

    # Map tickers to their indices for later use
    ticker_indices = {ticker: idx for idx, ticker in enumerate(tickers)}

    # Fetch historical data for all tickers
    date = '20240925 00:00:00'  # End date for historical data
    history_period = '1 D'  # Historical period to fetch
    bar_size = '5 mins'  # Bar size

    historical_data_df = fetch_historical_data_for_sp500(tickers, date, history_period, bar_size, ticker_indices)

    # Rename 'Index' column to 'Ticker Index' before saving
    historical_data_df = historical_data_df.rename(columns={'Index': 'Ticker Index'})

    # Print the DataFrame
    print(historical_data_df)
    print(historical_data_df.columns)

    # Specify the table name where data should be saved
    save_table = 'historical_data_sp500'

    # Call the save function to save the DataFrame to MySQL
    save_dataframe_to_mysql(historical_data_df, db_url, save_table)


if __name__ == "__main__":
    main()
