from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from time import sleep


class IBApi(EWrapper, EClient):
    def __init__(self, ticker, action, order_type, lmt_price, total_quantity):
        EClient.__init__(self, self)
        self.ticker = ticker
        self.action = action
        self.order_type = order_type
        self.lmt_price = lmt_price
        self.total_quantity = total_quantity
        self.contract = self.create_contract()
        self.parent_order = self.create_parent_order()
        self.stop_loss_order = self.create_stop_loss_order()

    def create_contract(self):
        contract = Contract()
        contract.symbol = self.ticker
        contract.secType = 'STK'
        contract.exchange = 'SMART'
        contract.currency = 'USD'
        return contract

    def create_parent_order(self):
        parent_order = Order()
        parent_order.action = self.action
        parent_order.orderType = self.order_type
        parent_order.totalQuantity = self.total_quantity
        parent_order.lmtPrice = self.lmt_price
        parent_order.eTradeOnly = False
        parent_order.firmQuoteOnly = False
        return parent_order

    def create_stop_loss_order(self):
        stop_loss_order = Order()
        stop_loss_order.action = "SELL" if self.parent_order.action == "BUY" else "BUY"
        stop_loss_order.orderType = "TRAIL"
        stop_loss_order.totalQuantity = self.parent_order.totalQuantity
        stop_loss_order.auxPrice = self.lmt_price * 0.95
        stop_loss_order.parentId = self.parent_order.orderId
        stop_loss_order.adjustableTrailingUnit = 100
        stop_loss_order.adjustedTrailingAmount = 1
        stop_loss_order.eTradeOnly = False
        stop_loss_order.firmQuoteOnly = False
        return stop_loss_order

    def nextValidId(self, orderId):
        self.nextOrderId = orderId
        self.start()

    def start(self):
        self.placeOrder(self.nextOrderId, self.contract, self.parent_order)
        sleep(1)
        self.placeOrder(self.nextOrderId + 1, self.contract, self.stop_loss_order)
        sleep(1)
        self.disconnect()


class IBOrderManager:
    def __init__(self, ticker, action, order_type, lmt_price, total_quantity):
        self.ticker = ticker
        self.action = action
        self.order_type = order_type
        self.lmt_price = lmt_price
        self.total_quantity = total_quantity

    def send_order(self):
        app = IBApi(self.ticker, self.action, self.order_type, self.lmt_price, self.total_quantity)
        app.connect('127.0.0.1', 7497, 0)
        app.run()


def main():
    order_manager = IBOrderManager('AAPL', 'BUY', 'LMT', 200, 100)
    order_manager.send_order()


if __name__ == "__main__":
    main()
