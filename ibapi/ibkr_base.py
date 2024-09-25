from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from time import sleep


class IBBase(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextOrderId = None
    
    def nextValidId(self, orderId):
        self.nextOrderId = orderId
        self.start()

    def start(self):
        raise NotImplementedError("This method should be overridden by subclasses.")
    
    def create_contract(self, symbol, sec_type="STK", exchange="SMART", currency="USD"):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = sec_type
        contract.exchange = exchange
        contract.currency = currency
        return contract

    def connect_client(self):
        self.connect('127.0.0.1', 7497, 0)

    def run_client(self):
        self.connect_client()
        self.run()

    def disconnect_client(self):
        self.disconnect()
