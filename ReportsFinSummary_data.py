from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import time

class TestApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

        self.firstReqId = 8001 # remember starting id
        self.contracts={} # keep in dict so you can lookup
        self.contNumber = self.firstReqId 

    def addContracts(self, cont):
        self.contracts[self.contNumber]=cont # add to dict using 8001 first time
        self.contNumber+=1 # next id will be 8002 etc.

    def nextValidId(self, orderId:int):
        # now you are connected, ask for data, no need for sleeps
        # this isn't the only way to know the api is started but it's what IB recommends
        self.contNumber = self.firstReqId # start with first reqId
        self.getNextData()

    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, "", errorCode, "", errorString)

        # if there was an error in one of your requests, just contimue with next id
        if reqId > 0 and self.contracts.get(self.contNumber):
            # err in reqFundametalData based on reqid existing in map
            print('err in', self.contracts[reqId].symbol)
            self.getNextData() # try next one

    def fundamentalData(self, reqId, fundamental_data):
        # note no need for globals, we have a dict of contracts
        Filename = self.contracts[reqId].symbol + '_ReportsFinSummary.xml'
        print("Filename: ", Filename)
        f_out = open(Filename, "w")
        f_out.write(fundamental_data)
        f_out.close()
        self.getNextData() # finished on request see if there are more

    def getNextData(self):
        if self.contracts.get(self.contNumber):# means a contract exists
            # so req data
            self.reqFundamentalData(self.contNumber, self.contracts[self.contNumber], "ReportsFinSummary", [])
            self.contNumber += 1 # now get ready for next request
        else: # means no more sequentially numbered contracts
            print('done')
            self.disconnect() # just exit

def main():
    app = TestApp() #just instantiate, don't run

    # The input file need to contain in each line: company ticker,currency,exchange - no spaces between them
    #Company_tickers = open("IB_FD_input.txt", 'r').readlines()  # reads a file with companies tickers in one column
    Company_tickers = ['META,USD,','AAPL,USD,']
    #print("Company_tickers: ", Company_tickers)
    Number_compnaies = len(Company_tickers)
    Company_count = 0
    for stock in Company_tickers:
        aa = stock.split(",")
        Symbol = aa[0].replace(" ", "")  # in case there is a space
        Currency = aa[1].replace(" ", "")
        Exchange = aa[2].replace("\n", "").replace(" ","")  # need to remove the \n as it is the last field in the entry line
        contract = Contract()  # defining the stock to download the fundamental data from IB
        contract.symbol = Symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = Currency
        contract.primaryExchange = Exchange
        print("Contract: ", contract)

        Company_count += 1  # To show progress on screen
        print("\n\n" + "**********************" + "\n")
        print("  " + Symbol + ": # " + str(Company_count) + " / " + str(Number_compnaies))
        print("\n" + "**********************" + "\n")

        #add the contracts to apps dict  
        app.addContracts(contract)

    app.connect("127.0.0.1", 7497, 123)
    # this method will start a socket read loop and will block until disconnect
    app.run()

main()