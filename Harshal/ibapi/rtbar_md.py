from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import Contract

from decimal import *

import time

class TradeApp(EWrapper, EClient): 
    def __init__(self): 
        EClient.__init__(self, self) 

    def realtimeBar(self, reqId: TickerId, time:int, open_: float, high: float, low: float, close: float, volume: Decimal, wap: Decimal, count: int):
        print("RealTimeBar. TickerId:", reqId, RealTimeBar(time, -1, open_, high, low, close, volume, wap, count))
    
app = TradeApp()      
app.connect("127.0.0.1", 7497, clientId=1)

contract = Contract() 
contract.symbol = "AAPL" 
contract.secType = "STK" 
contract.currency = "USD" 
contract.exchange = "SMART" 

app.reqRealTimeBars(3001, contract, 5, "TRADES", 0, [])

app.run()