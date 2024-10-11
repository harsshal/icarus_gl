# https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/#hist-duration

import pandas as pd
from ibkr_base import IBBase
from time import sleep


class IBHistoricalData(IBBase):
    def __init__(self, ticker, endDateTime, durationStr, barSizeSetting, primaryExchange="SMART"):
        super().__init__()
        self.ticker = ticker
        self.endDateTime = endDateTime
        self.durationStr = durationStr
        self.barSizeSetting = barSizeSetting
        self.primaryExchange = primaryExchange
        self.data = []

    def start(self):
        contract = self.create_contract(self.ticker, self.primaryExchange)
        #self.reqHistoricalData(1, contract, self.endDateTime, self.durationStr,
        #                       self.bar_size, 'TRADES', 1, 1, False, [])
        
        keepUpToDate = False
        
        if self.endDateTime == '':
            keepUpToDate = True

        self.reqHistoricalData(reqId=101, 
                        contract=contract,
                        endDateTime=self.endDateTime, 
                        durationStr=self.durationStr,
                        barSizeSetting=self.barSizeSetting,
                        whatToShow='Trades',
                        useRTH=0,                 #0 = Includes data outside of RTH | 1 = RTH data only 
                        formatDate=1,    
                        keepUpToDate=keepUpToDate,           #0 = False | 1 = True 
                        chartOptions=[])

        sleep(1)
        self.disconnect_client()

    def historicalData(self, reqId, bar):
        self.data.append(bar)

    def historicalDataEnd(self, reqId, start, end):
        self.disconnect_client()
        attributes = vars(self.data[0]).keys() if self.data else []
        df = pd.DataFrame([{attr.title(): getattr(bar, attr) for attr in attributes}
                           for bar in self.data])
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize('America/New_York')
        self.data = df.set_index('Date') if not df.empty else pd.DataFrame()


def get_ibkr_data(ticker,endDateTime='', 
                        durationStr='1 D',
                        barSizeSetting='1 hour',
                        primaryExchange="SMART"):
    app = IBHistoricalData(ticker, endDateTime, durationStr, barSizeSetting, primaryExchange)
    app.run_client()
    if len(app.data) == 0:
        print("No data received for ticker: " + ticker)
        return pd.DataFrame()
    return app.data


def main():
    df = get_ibkr_data('AAPL', '20240931 00:00:00 US/Eastern', '1 D', '1 min')
    print(df.tail(10))
    df = get_ibkr_data('AAPL', '', '1 D', '1 min')
    print(df.tail(10))


if __name__ == "__main__":
    main()
