import time
from datetime import datetime, timedelta
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Sentiment analysis tool
sia = SentimentIntensityAnalyzer()

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.news_data = []

    def error(self, reqId, errorCode, errorString):
        print(f"Error {reqId}: {errorCode} - {errorString}")

    def newsProviders(self, newsProviders):
        print("Available news providers:")
        for provider in newsProviders:
            print(f"Provider: {provider}")

    def tickNews(self, tickerId: int, timeStamp: int, providerCode: str, articleId: str, headline: str, extraData: str):
        print("TickNews. TickerId:", tickerId, "TimeStamp:", timeStamp, "ProviderCode:", providerCode, "ArticleId:", articleId, "Headline:", headline, "ExtraData:", extraData)
        # Analyze sentiment
        sentiment = sia.polarity_scores(headline)
        print(f"Sentiment Score: {sentiment}\n")

def main():
    # Initialize the API client
    app = IBapi()

    # Connect to the TWS or IB Gateway (Make sure TWS/IB Gateway is running)
    app.connect('127.0.0.1', 7497, clientId=1)

    # Wait for connection to complete
    time.sleep(3)  # Give time for the connection to be established

    # Request available news providers
    app.reqNewsProviders()

    # Give the client some time to get news providers response
    time.sleep(1)

    # Set up the contract for news
    contract = Contract()
    contract.symbol = "BRFG:BRFG_ALL"
    contract.secType = "NEWS"
    contract.exchange = "BRFG"

    # Request market data for the news (subscribing to the news feed)
    reqId = 1  # Replace with actual request ID if needed
    app.reqMktData(reqId, contract, "", False, False, [])

    # Keep the application running to receive responses
    app.run()

if __name__ == "__main__":
    main()
