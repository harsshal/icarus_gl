from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd


class IBApi(EWrapper, EClient):
    def __init__(self, ticker, end_date, history_period, bar_size):
        EClient.__init__(self, self)
        self.ticker = ticker
        self.end_date = end_date
        self.history_period = history_period
        self.bar_size = bar_size
        self.data = []

    def nextValidId(self, orderId):
        self.request_historical_data()

    def request_historical_data(self):
        contract = self.create_contract()
        # Request historical data
        self.reqHistoricalData(1, contract, self.end_date, self.history_period, 
                               self.bar_size, 'TRADES', 1, 1, False, [])

    def create_contract(self):
        contract = Contract()
        contract.symbol = self.ticker
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'
        return contract

    def historicalData(self, reqId, bar):
        self.data.append(bar)

    def historicalDataEnd(self, reqId, start, end):
        self.disconnect()
        self.process_historical_data()

    def process_historical_data(self):
        # Extract attributes from the first element of self.data
        attributes = vars(self.data[0]).keys() if self.data else []

        # Create a DataFrame using the extracted attributes
        df = pd.DataFrame([{attr.title(): getattr(bar, attr) for attr in attributes} 
                           for bar in self.data])

        # Convert 'Date' to New York timezone and set as index
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize('America/New_York')
        self.df = df.set_index('Date') if not df.empty else pd.DataFrame()

    def get_df(self):
        return self.df if hasattr(self, 'df') else pd.DataFrame()


def get_ibkr_data(ticker, end_date, history_period, bar_size):
    app = IBApi(ticker, end_date, history_period, bar_size)
    app.connect('127.0.0.1', 7497, 0)
    app.run()
    return app.get_df()


# TODO : add a function to get realtime data as well

def main():
    df = get_ibkr_data('AAPL', '20240631 00:00:00', '1 D', '1 min')
    print(df.tail(10))


if __name__ == "__main__":
    main()
