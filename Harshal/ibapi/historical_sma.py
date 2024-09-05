from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import pandas as pd
import numpy as np

class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []
        self.nextOrderId = None
        self.historical_data_end = False

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
        self.reqHistoricalData(1, contract, '', '300 D', '1 day', 'MIDPOINT', 1, 1, False, [])

    def historicalData(self, reqId, bar):
        self.data.append(bar)

    def historicalDataEnd(self, reqId, start, end):
        self.historical_data_end = True
        self.calculate_indicators()

    def calculate_indicators(self):
        #df = pd.DataFrame(self.data)
        df = pd.DataFrame(list(map(lambda x:[x.close,x.date],self.data))
                          ,columns=["close","date"])

        df['SMA_short'] = df['close'].rolling(window=10).mean()
        df['SMA_long'] = df['close'].rolling(window=30).mean()

        df['signal'] = 0
        df['signal'] = np.where(df['SMA_short'] > df['SMA_long'], 1, 0)
        #df['signal'][10:] = np.where(df['SMA_short'][10:] > df['SMA_long'][10:], 1, 0)
        df['position'] = df['signal'].diff()

        print(df)

        self.execute_trades(df)

    def execute_trades(self, df):
        contract = Contract()
        contract.symbol = 'AAPL'
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'

        for i in range(len(df)):
            if df['position'].iloc[i] == 1:
                print(f"Buy signal on {df['date'].iloc[i]}: {df['close'].iloc[i]}")
                order = Order()
                order.action = 'BUY'
                order.orderType = 'MKT'
                order.totalQuantity = 100
                order.eTradeOnly = False
                order.firmQuoteOnly = False
                self.placeOrder(self.nextOrderId, contract, order)
                self.nextOrderId += 1
            elif df['position'].iloc[i] == -1:
                print(f"Sell signal on {df['date'].iloc[i]}: {df['close'].iloc[i]}")
                order = Order()
                order.action = 'SELL'
                order.orderType = 'MKT'
                order.totalQuantity = 100
                order.eTradeOnly = False
                order.firmQuoteOnly = False
                self.placeOrder(self.nextOrderId, contract, order)
                self.nextOrderId += 1

        self.disconnect()

def main():
    app = IBApi()
    app.connect('127.0.0.1', 7497, 0)
    app.run()

if __name__ == "__main__":
    main()
