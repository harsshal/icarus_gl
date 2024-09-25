from ibapi.contract import Contract
from ibkr_base import IBBase  # Import the IBBase module
from datetime import datetime
import threading
import time


class IBApiNews(IBBase):
    def __init__(self, ticker):
        # Initialize IBBase and set the ticker for news requests
        super().__init__()
        self.ticker = ticker
        self.news_data = []
        self.news_flag = False

    def start(self):
        # Create a contract for the news subscription
        contract = Contract()
        contract.symbol = self.ticker  # Only use the ticker
        contract.secType = "STK"       # Stock security type for the ticker
        contract.exchange = "SMART"    # Exchange
        contract.currency = "USD"      # Currency

        # Request live news bulletins, set allMsgs to True to receive all news types
        self.reqNewsBulletins(allMsgs=True)

    # Handle news bulletins
    def newsBulletins(self, msgId: int, newsType: int, newsMsg: str, originExch: str):
        news_time = datetime.utcnow()  # Get the current UTC time

        # Store the news if it's breaking or important
        news_entry = {
            'time': news_time,
            'message': newsMsg,
            'exchange': originExch,
            'type': newsType,
        }
        self.news_data.append(news_entry)
        self.news_flag = True
        print(f"Breaking news for {self.ticker}: {newsMsg}")

    def has_recent_news(self):
        # Check if any breaking news has been detected
        return self.news_flag


# Function to get news for a specific ticker using IBApiNews class
def get_ibkr_news(ticker):
    app = IBApiNews(ticker)

    # Start the API client
    threading.Thread(target=app.run_client).start()

    # Sleep for 5 seconds before terminating the client
    time.sleep(5)

    # Stop the client after 5 seconds
    app.disconnect_client()

    # Check if there's recent breaking news
    return app.has_recent_news()


# Example usage if run standalone
if __name__ == "__main__":
    
    #TODO : need to get all the tickers which have top news
    ticker = "SPX"
    has_news = get_ibkr_news(ticker)
    print(f"Breaking news detected for {ticker}: {has_news}")
