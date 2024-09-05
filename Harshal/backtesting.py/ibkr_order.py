from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import pandas as pd

class IBApi(EWrapper, EClient):
    def __init__(self, ticker, action, order_type, lmt_price, total_quantity):
        #print("init")
        EClient.__init__(self, self)
        self.data = []
        self.df = pd.DataFrame()
        self.nextOrderId = None

        contract = Contract()
        contract.symbol = ticker
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'
        self.contract = contract

        # Define the contract
        contract = Contract()
        contract.symbol = ticker
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'
        self.contract = contract

        # Define the parent order
        parent_order = Order()
        parent_order.action = action
        parent_order.orderType = order_type
        parent_order.totalQuantity = total_quantity
        parent_order.lmtPrice = lmt_price
        parent_order.eTradeOnly = False
        parent_order.firmQuoteOnly = False
        
        self.parent_order = parent_order

        # Define the stop loss order
        stop_loss_order = Order()
        stop_loss_order.action = "SELL" if parent_order.action == "BUY" else "BUY"
        stop_loss_order.orderType = "TRAIL"
        stop_loss_order.totalQuantity = parent_order.totalQuantity
        stop_loss_order.auxPrice = lmt_price * 0.95
        stop_loss_order.parentId = parent_order.orderId
        #With a stop price of...
        #stop_loss_order.adjustedStopPrice = lmt_price * 0.95
        #traling by and amount (0) or a percent (100)...
        stop_loss_order.adjustableTrailingUnit = 100
        #of...
        stop_loss_order.adjustedTrailingAmount = 1
        stop_loss_order.eTradeOnly = False
        stop_loss_order.firmQuoteOnly = False


        self.stop_loss_order = stop_loss_order


    def nextValidId(self, orderId):
        #print("nextValidId: %s" % orderId)
        self.nextOrderId = orderId
        self.start()

    def start(self):
        #print("start")
        self.placeOrder(self.nextOrderId, self.contract, self.parent_order)
        self.placeOrder(self.nextOrderId + 1, self.contract, self.stop_loss_order)
        self.disconnect()

def send_ibkr_order(ticker, action, order_type, lmt_price, total_quantity):
    app = IBApi(ticker, action, order_type, lmt_price, total_quantity)
    app.connect('127.0.0.1', 7497, 0)
    app.run()

def main():
    send_ibkr_order('AAPL','BUY','LMT',200, 100)

if __name__ == "__main__":
    main()
