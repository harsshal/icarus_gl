from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from threading import Thread
import pandas as pd
from datetime import datetime
import time
from sqlalchemy import create_engine


class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.current_price = {}
        self.reqId_counter = 1  # Initialize request ID counter

    def error(self, reqId, errorCode, errorString):
        print(f"Error {reqId}: {errorCode} - {errorString}")

    def tickPrice(self, reqId, tickType, price, attrib):
        if tickType == 4:  # Last price tick (use tickType 4 for last price)
            print(f"Received price for reqId {reqId}: {price}")
            self.current_price[reqId] = price

    def get_current_price(self, ticker):
        contract = self.create_stock_contract(ticker)
        reqId = self.reqId_counter  # Use unique request ID
        self.reqMktData(reqId, contract, "", False, False, [])
        self.reqId_counter += 1  # Increment request ID for next request

        # Wait for IBKR API to fetch the price
        time.sleep(5)
        self.cancelMktData(reqId)  # Stop receiving market data
        
        # Return the fetched price or None if not found
        return self.current_price.get(reqId, None)

    def create_stock_contract(self, symbol):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = 'STK'  # Security type: stock
        contract.exchange = 'SMART'  # Use SMART routing for stock
        contract.currency = 'USD'  # USD currency
        return contract


def fetch_current_prices(tickers):
    """
    Fetch the current prices for a list of ticker symbols using IBKR API
    and store the results in a DataFrame with columns: date, time, ticker, price.
    
    Parameters:
    - tickers: list of ticker symbols
    
    Returns:
    A DataFrame containing the current price, date, and time for each ticker.
    """
    # Create an empty DataFrame to store results
    columns = ['date', 'time', 'ticker', 'price']
    price_df = pd.DataFrame(columns=columns)

    # Initialize IBKR API client
    app = IBApi()
    app.connect('127.0.0.1', 7497, 0)  # Connect to TWS or IBKR Gateway
    app_thread = Thread(target=app.run)
    app_thread.start()

    # List to collect rows of data
    rows = []

    for ticker in tickers:
        price = app.get_current_price(ticker)
        print(f"Fetched price for {ticker}: {price}")  # Debugging print
        if price is not None:
            now = datetime.now()  # Get current date and time
            date = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            
            # Append data as a dictionary (row)
            rows.append({
                'date': date,
                'time': time_str,
                'ticker': ticker,
                'price': price
            })

    # Combine all rows into a DataFrame
    if rows:
        price_df = pd.DataFrame(rows)

    # Disconnect from IBKR after fetching all prices
    app.disconnect()
    app_thread.join()

    return price_df


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


def main():
    # Specify the MySQL database connection URL and table name
    db_url = 'mysql+pymysql://icarus-user:gl_icarus@localhost/interactive_data'
    table_name = 'sp500_tickers'

   
    tickers = get_tickers_from_sql(db_url, table_name)
    print(f"Tickers fetched from SQL: {tickers}")  # Debugging print

    # Fetch current prices and store them in a DataFrame
    price_df = fetch_current_prices(tickers)

    print(price_df)






if __name__ == "__main__":
    main()
