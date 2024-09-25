from ibapi.order import Order
from ibkr_base import IBBase
from time import sleep


class IBOrder(IBBase):
    def __init__(self, ticker, action, order_type, lmt_price, total_quantity):
        super().__init__()
        self.ticker = ticker
        self.action = action
        self.order_type = order_type
        self.lmt_price = lmt_price
        self.total_quantity = total_quantity
        self.contract = self.create_contract(self.ticker)
        self.parent_order = self.create_parent_order()
        self.stop_loss_order = self.create_stop_loss_order()

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

    def start(self):
        self.placeOrder(self.nextOrderId, self.contract, self.parent_order)
        sleep(1)
        self.placeOrder(self.nextOrderId + 1, self.contract, self.stop_loss_order)
        sleep(1)
        self.disconnect_client()


def main():
    app = IBOrder('AAPL', 'BUY', 'LMT', 200, 100)
    app.run_client()


if __name__ == "__main__":
    main()
