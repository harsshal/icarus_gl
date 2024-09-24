import pandas as pd
from ibkr_base import IBBase


class IBHistoricalData(IBBase):
    def __init__(self, ticker, end_date, history_period, bar_size):
        super().__init__()
        self.ticker = ticker
        self.end_date = end_date
        self.history_period = history_period
        self.bar_size = bar_size
        self.data = []

    def nextValidId(self, orderId):
        self.request_historical_data()

    def request_historical_data(self):
        contract = self.create_contract(self.ticker)
        self.reqHistoricalData(1, contract, self.end_date, self.history_period,
                               self.bar_size, 'TRADES', 1, 1, False, [])

    def historicalData(self, reqId, bar):
        self.data.append(bar)

    def historicalDataEnd(self, reqId, start, end):
        self.disconnect_client()
        self.process_historical_data()

    def process_historical_data(self):
        attributes = vars(self.data[0]).keys() if self.data else []
        df = pd.DataFrame([{attr.title(): getattr(bar, attr) for attr in attributes}
                           for bar in self.data])
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize('America/New_York')
        self.df = df.set_index('Date') if not df.empty else pd.DataFrame()

    def get_df(self):
        return getattr(self, 'df', pd.DataFrame())


def get_ibkr_data(ticker, end_date, history_period, bar_size):
    app = IBHistoricalData(ticker, end_date, history_period, bar_size)
    app.run_client()
    return app.get_df()


def main():
    df = get_ibkr_data('AAPL', '20240631 00:00:00', '1 D', '1 min')
    print(df.tail(10))


if __name__ == "__main__":
    main()
