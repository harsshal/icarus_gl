from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import time


class IBApi(EWrapper, EClient):
    def __init__(self):
        print("initializing strategy")
        EClient.__init__(self, self)
        self.data = []
        self.df = pd.DataFrame()
        self.nextOrderId = None

    def nextValidId(self, orderId):
        self.nextOrderId = orderId
        self.start()

    def start(self):
        contract = Contract()
        contract.symbol = 'AAPL'
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'

        # Request historical data
        self.reqHistoricalData(1, contract, '', '1 D', '1 min', 'ADJUSTED_LAST', 1, 1, False, [])
        self.reqRealTimeBars(2, contract, 60, 'TRADES', True, [])
        time.sleep(11)

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
        #df['Date'] = pd.to_datetime(df['Date'])

        self.df = df.set_index(['Date'])

        print(self.df.tail(10))

    def realtimeBar(self, reqId, time, open_, high, low, close, volume, wap, count):
        print("Got an RTBAR", time)
        new_row = pd.DataFrame({
            'Date': [pd.to_datetime(time, unit='s').tz_localize('UTC').tz_convert('America/New_York')],
            'Open': [open_],
            'High': [high],
            'Low': [low],
            'Close': [close],
            'Volume': [volume],
            'Barcount': [count],
            'Average': [wap]
        })
        new_row.set_index('Date', inplace=True)
        #print(new_row)
        self.df = pd.concat([self.df, new_row])
        print(self.df.tail(10))

        # Resample the dataframe to 1-minute intervals
        df_resampled = self.df.resample('1T').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum',
            'Barcount': 'sum',
            'Average': 'mean'
        }).dropna(how='all')

        print(df_resampled.tail(10))

def main():
    app = IBApi()
    app.connect('127.0.0.1', 7497, 0)
    app.run()

if __name__ == "__main__":
    main()
