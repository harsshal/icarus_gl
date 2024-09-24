from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.common import BarData
import pandas as pd
import numpy as np

class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []
        self.nextOrderId = None
        self.historical_data_end = False
        self.df = pd.DataFrame()

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
        self.reqHistoricalData(1, contract, '', '1 D', '5 mins', 'MIDPOINT', 1, 1, False, [])
        self.reqRealTimeBars(2, contract, 5, "MIDPOINT", True, [])

    def historicalData(self, reqId, bar):
        self.data.append([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])

    def historicalDataEnd(self, reqId, start, end):
        self.historical_data_end = True
        self.df = pd.DataFrame(self.data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        self.calculate_indicators()

    def realtimeBar(self, reqId, time, open_, high, low, close, volume, wap, count):
        new_row = {'date': pd.to_datetime(time, unit='s'), 'open': open_, 'high': high, 'low': low, 'close': close, 'volume': volume}
        self.df = pd.concat([self.df, pd.DataFrame(new_row, index=[0])], ignore_index=True)
        self.calculate_indicators()

    def calculate_indicators(self):
        self.df['SMA_short'] = self.df['close'].rolling(window=3).mean()
        self.df['SMA_long'] = self.df['close'].rolling(window=6).mean()

        self.df['signal'] = 0
        self.df['signal'] = np.where(self.df['SMA_short'] > self.df['SMA_long'], 1, 0)
        self.df['position'] = self.df['signal'].diff()

        self.execute_trades()

    def execute_trades(self):
        contract = Contract()
        contract.symbol = 'AAPL'
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'

        if not self.df.empty:
            last_position = self.df.iloc[-1]['position']
            last_date = self.df.iloc[-1]['date']
            last_close = self.df.iloc[-1]['close']

            if last_position == 1:
                print(f"Buy signal on {last_date}: {last_close}")
                order = Order()
                order.action = 'BUY'
                order.orderType = 'MKT'
                order.totalQuantity = 100
                order.eTradeOnly = False
                order.firmQuoteOnly = False
                self.placeOrder(self.nextOrderId, contract, order)
                self.nextOrderId += 1
            elif last_position == -1:
                print(f"Sell signal on {last_date}: {last_close}")
                order = Order()
                order.action = 'SELL'
                order.orderType = 'MKT'
                order.totalQuantity = 100
                order.eTradeOnly = False
                order.firmQuoteOnly = False
                self.placeOrder(self.nextOrderId, contract, order)
                self.nextOrderId += 1

        print(self.df.tail())

def main():
    app = IBApi()
    app.connect('127.0.0.1', 7497, 0)
    app.run()

if __name__ == "__main__":
    main()
