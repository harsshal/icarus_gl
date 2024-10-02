# https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/#hist-duration

import pandas as pd
from ibkr_base import IBBase


class IBHistoricalData(IBBase):
    def __init__(self, ticker, endDateTime, durationStr, barSizeSetting):
        super().__init__()
        self.ticker = ticker
        self.endDateTime = endDateTime
        self.durationStr = durationStr
        self.barSizeSetting = barSizeSetting
        self.data = []

    def nextValidId(self, orderId):
        self.request_historical_data()

    def request_historical_data(self):
        contract = self.create_contract(self.ticker)
        #self.reqHistoricalData(1, contract, self.endDateTime, self.durationStr,
        #                       self.bar_size, 'TRADES', 1, 1, False, [])
        
        self.reqHistoricalData(reqId=101, 
                          contract=contract,
                          endDateTime=self.endDateTime, 
                          durationStr=self.durationStr,
                          barSizeSetting=self.barSizeSetting,
                          whatToShow='Trades',
                          useRTH=0,                 #0 = Includes data outside of RTH | 1 = RTH data only 
                          formatDate=1,    
                          keepUpToDate=0,           #0 = False | 1 = True 
                          chartOptions=[])

    def historicalData(self, reqId, bar):
        self.data.append(bar)

    def historicalDataEnd(self, reqId, start, end):
        self.disconnect_client()
        self.process_historical_data()

    def process_historical_data(self):
        attributes = vars(self.data[0]).keys() if self.data else []
        df = pd.DataFrame([{attr.title(): getattr(bar, attr) for attr in attributes}
                           for bar in self.data])
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize('America/New_York')
        self.df = df.set_index('Date') if not df.empty else pd.DataFrame()

    def get_df(self):
        return getattr(self, 'df', pd.DataFrame())


def get_ibkr_data(ticker, endDateTime='', 
                          durationStr='1 D',
                          barSizeSetting='1 hour',):
    app = IBHistoricalData(ticker, endDateTime, durationStr, barSizeSetting)
    app.run_client()
    return app.get_df()


def main():
    df = get_ibkr_data('AAPL', '20240931 00:00:00 US/Eastern', '1 D', '1 min')
    print(df.tail(10))


if __name__ == "__main__":
    main()
