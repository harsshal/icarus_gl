import yfinance as yf
import pandas as pd

def get_sp500_tickers():
    """
    This function fetches the ticker symbols and company names of S&P 500 companies.
    It returns a DataFrame with columns: 'Ticker' and 'Company Name'.
    """
    # Download the list of S&P 500 companies from Wikipedia
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    table = pd.read_html(url)[0]  # The first table is the S&P 500 table

    # Select the 'Symbol' and 'Security' columns from the table
    sp500_df = table[['Symbol', 'Security']].rename(columns={'Symbol': 'Ticker', 'Security': 'Company Name'})
    
    return sp500_df

def main():
    # Get the DataFrame of S&P 500 companies
    sp500_df = get_sp500_tickers()

    print(sp500_df.head())

if __name__ == "__main__":
    main()
