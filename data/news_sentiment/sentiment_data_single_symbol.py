import time
from datetime import datetime, timedelta
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
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

    def historicalNews(self, reqId, time, providerCode, articleId, headline):
        print(f"News: {time} - {headline}")
        self.news_data.append((providerCode, articleId, headline))

    def newsArticle(self, reqId, articleType, articleText):
        print(f"Full News Article: {articleText}")
        # Analyze sentiment
        sentiment = sia.polarity_scores(articleText)
        print(f"Sentiment Score: {sentiment}\n")

    def historicalNewsEnd(self, reqId, hasMore):
        print("End of historical news")
        self.disconnect()

def main():
    # Initialize the API client
    app = IBapi()

    # Connect to the TWS or IB Gateway (Make sure TWS/IB Gateway is running)
    app.connect('127.0.0.1', 7497, clientId=1)

    # Wait for connection to complete
    time.sleep(3)  # Increased sleep to allow connection setup

    # Request available news providers
    app.reqNewsProviders()

    # Give the client some time to get news providers response
    time.sleep(1)

    # Get the current time and 5 minutes earlier
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=5)

    # Convert datetime to IB string format
    end_time_str = end_time.strftime("%Y%m%d %H:%M:%S")
    start_time_str = start_time.strftime("%Y%m%d %H:%M:%S")

    # Replace '8314' with the actual contract ID (conId) for the news provider
    conId = 8314  # Placeholder

    # Assuming the news provider code "BRFG" exists, otherwise adjust as needed
    provider_code = 'BRFG'
    provider_code = 'BRFUPDN'
    provider_code = 'DJNL'

    # Request historical news (updated to 7 parameters)
    app.reqHistoricalNews(1, conId, provider_code, start_time_str, end_time_str, 10, [])

    # Keep the application running to receive responses
    app.run()

if __name__ == "__main__":
    main()
