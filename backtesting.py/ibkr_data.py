from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd

class IBApi(EWrapper, EClient):
    def __init__(self, ticker, end_date,history_period, bar_size):
        #print("initializing strategy")
        EClient.__init__(self, self)
        self.data = []
        self.df = pd.DataFrame()

        self.ticker = ticker
        self.history_period = history_period
        self.bar_size = bar_size
        self.end_date = end_date

    def nextValidId(self, orderId):
        self.start()

    def start(self):
        contract = Contract()
        contract.symbol = self.ticker
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'

        # Request historical data
        self.reqHistoricalData(1, contract, self.end_date, self.history_period, self.bar_size, 'TRADES', 1, 1, False, [])

    def historicalData(self, reqId, bar):
        self.data.append(bar)

    def historicalDataEnd(self, reqId, start, end):
        self.historical_data_end = True
        self.disconnect()
        # Extract attributes from the first element of self.data
        attributes = vars(self.data[0]).keys()

        # Create a DataFrame using the extracted attributes
        df = pd.DataFrame([{attr.title(): getattr(bar, attr) for attr in attributes} for bar in self.data])

        # historical data is in TWS timezone where as real time data is in UTC
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize('America/New_York')

        self.df = df.set_index(['Date'])

        #print(self.df.tail(10))

def get_ibkr_data(ticker,end_date, history_period, bar_size):
    app = IBApi(ticker, end_date, history_period, bar_size)
    app.connect('127.0.0.1', 7497, 0)
    app.run()
    return app.df

def main():
    print(get_ibkr_data('AAPL','20240631 00:00:00','1 D', '1 min'))

if __name__ == "__main__":
    main()
