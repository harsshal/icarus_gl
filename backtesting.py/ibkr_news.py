from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from datetime import datetime, timedelta

class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.news_data = []

    def nextValidId(self, orderId: int):
        print(f"Next valid orderId: {orderId}")
        self.request_news_data()

    def request_news_data(self):
        contract = Contract()
        contract.symbol = "BRFG:BRFG_ALL"  
        contract.secType = "NEWS"
        contract.exchange = "BRFG"

        self.reqMktData(1001, contract, "mdoff,292", False, False, [])

    # Handle the live news headlines
    def tickNews(self, tickerId: int, timeStamp: int, providerCode: str, articleId: str, headline: str, extraData: str):
        news_time = timeStamp
        #current_time = datetime.utcnow()

        # Check if the news is from the last 5 minutes
        #if current_time - news_time <= timedelta(minutes=5):
        print("TickNews. TickerId:", tickerId, "TimeStamp:", timeStamp, "ProviderCode:", providerCode, "ArticleId:", articleId, "Headline:", headline, "ExtraData:", extraData)

    def historicalNewsEnd(self, requestId: int, hasMore: bool):
        print(f"Historical news request {requestId} finished. More news available: {hasMore}")

def main():
    app = IBApi()
    app.connect("127.0.0.1", 7497, 0)
    app.run()

if __name__ == "__main__":
    main()
