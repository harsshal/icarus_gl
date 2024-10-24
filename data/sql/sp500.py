
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
import os

def get_sp500_tickers():
    """
    This function fetches the ticker symbols and company names of S&P 500 companies.
    It returns a DataFrame with columns: 'id', 'symbol', 'name', 'born', 'dead'.
    """
    # Download the list of S&P 500 companies from Wikipedia
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    table = pd.read_html(url)[0]  # The first table is the S&P 500 table

    # Select the 'Symbol' and 'Security' columns from the table
    sp500_df = table[['Symbol', 'Security']].rename(columns={'Symbol': 'symbol', 'Security': 'name'})

    # Add 'id' column (index as ID starting from 1)
    sp500_df['id'] = sp500_df.index + 1

    # Fetch IPO (born) dates from Yahoo Finance
    sp500_df['born'] = sp500_df['symbol'].apply(get_ipo_date)

    sp500_df['born'] = sp500_df['born'].fillna('0001-01-01')

    # Set 'dead' to None for now 
    sp500_df['dead'] = '3000-01-01'

    # Reorder columns to match the desired order
    sp500_df = sp500_df[['id', 'symbol', 'name', 'born', 'dead']]

    return sp500_df

def get_ipo_date(ticker):
    """
    Fetch the IPO (born) date for a given ticker symbol using Yahoo Finance.
    Returns the IPO date as a string, or None if unavailable.
    """
    try:
        # Use yfinance to get the ticker info
        stock = yf.Ticker(ticker)
        ipo_date = stock.info.get('ipoDate', None)
        
        # If the IPO date is not available, try to infer from the price history
        if ipo_date is None:
            # Use historical market data to estimate IPO date (first trading day available)
            hist = stock.history(period="max")
            if not hist.empty:
                ipo_date = hist.index[0].strftime('%Y-%m-%d')  # First available date in history
        return ipo_date
    except Exception as e:
        print(f"Error fetching IPO date for {ticker}: {e}")
        return None

def main():
    # Get the DataFrame of S&P 500 companies
    sp500_df = get_sp500_tickers()

    # Print the first few rows of the DataFrame
    print(sp500_df.head())

if __name__ == "__main__":
    main()
