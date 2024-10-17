from ibapi.client import *
from ibapi.wrapper import *

port = 7497

class TestApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self,self)

    def nextValidId(self, orderId: int):
        self.reqScannerParameters()
    
    def scannerParameters(self, xml):
        dir = "/Users/xinyangliu/Desktop/icar/icarus_gl/backtesting.py/scanner.xml"
        open(dir, 'w').write(xml)
        print("Scanner Parameters Received!")

app = TestApp()
app.connect("127.0.0.1", port, 1001)
app.run()

    
