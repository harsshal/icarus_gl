from ibapi.common import TickAttrib, TickerId
from ibapi.ticktype import TickType

import sys
import os

# Get the parent directory and add it to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from ibkr_base import IBBase
from ibkr_data import get_ibkr_data

class Momentum(IBBase):
    def __init__(self, ticker):
        super().__init__()
        self.ticker = ticker
        self.trade_data = []

    def start(self):
        self.contract = self.create_contract(self.ticker)

        # Request real-time market data
        # self.reqMktData(reqId=1, contract=self.contract, genericTickList="", snapshot=False, regulatorySnapshot=False, mktDataOptions=[])

        # Request historical market data
        print(get_ibkr_data(self.ticker, '20241002 11:55:00', '5 min', '1 tick'))
        self.disconnect_client()
        

    def tickPrice(self, reqId: int, tickType: int, price: float, attrib: TickAttrib):
        if tickType == 4:  # LAST price
            print(f"Last Trade Price: {price}")
            self.trade_data.append(price)
            if len(self.trade_data) >= 15:
                print("Last 15 trades: ", self.trade_data[-15:])
                self.disconnect_client()
    

def mean_reversion_price(trade_data):
    return sum(trade_data) / len(trade_data)

def momentum_price(trade_data):
    # using linear regression
    from sklearn.linear_model import LinearRegression
    import numpy as np
    X = np.array(range(len(trade_data))).reshape(-1, 1)
    y = trade_data
    model = LinearRegression().fit(X, y)
    return model.predict([[len(trade_data)]])

def main():
    app = Momentum('EGRX')
    app.run_client()

    print("Mean Reversion Price: ", mean_reversion_price(app.trade_data))
    print("Momentum Price: ", momentum_price(app.trade_data))


if __name__ == "__main__":
    main()