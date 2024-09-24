from ibapi.contract import Contract
from ibbase import IBBase  # Import the IBBase module
from datetime import datetime


class IBApiNews(IBBase):
    def __init__(self, ticker):
        # Initialize IBBase and set the ticker for news requests
        super().__init__()
        self.ticker = ticker
        self.news_data = []
        self.news_flag = False

    def nextValidId(self, orderId: int):
        # Request news data as soon as the connection is valid
        self.request_news_data()

    def request_news_data(self):
        # Create a contract for the news subscription
        contract = Contract()
        contract.symbol = f"{self.ticker}:BRFG_ALL"  # Assuming 'BRFG' is the news provider for IB
        contract.secType = "NEWS"
        contract.exchange = "BRFG"

        # Request live market data for news (news data is requested via market data for news contracts)
        self.reqMktData(1001, contract, "mdoff,292", False, False, [])

    # Handle live news headlines
    def tickNews(self, tickerId: int, timeStamp: int, providerCode: str, articleId: str, headline: str, extraData: str):
        news_time = datetime.utcfromtimestamp(timeStamp)

        # Store the news if it's breaking (for now, assume any news is important)
        news_entry = {
            'time': news_time,
            'headline': headline,
            'provider': providerCode,
            'articleId': articleId,
        }
        self.news_data.append(news_entry)
        self.news_flag = True
        print(f"Breaking news for {self.ticker}: {headline}")

    def has_recent_news(self):
        # Check if any breaking news has been detected
        return self.news_flag


# Function to get news for a specific ticker using IBApiNews class
def get_ibkr_news(ticker):
    app = IBApiNews(ticker)

    # Use the run_client method from IBBase to connect and run the event loop
    app.run_client()

    # Check if there's recent breaking news
    return app.has_recent_news()


# Example usage if run standalone
if __name__ == "__main__":
    ticker = "AAPL"
    has_news = get_ibkr_news(ticker)
    print(f"Breaking news detected for {ticker}: {has_news}")
