from sklearn.linear_model import LinearRegression
import numpy as np

import hputils
from ibkr_data import get_ibkr_data
from ibkr_order import IBOrder

def mean_reversion_price(trade_data):
    return sum(trade_data) / len(trade_data)

def momentum_price(trade_data):
    # using linear regression

    X = np.array(range(len(trade_data))).reshape(-1, 1)
    y = trade_data
    model = LinearRegression().fit(X, y)
    return model.predict([[len(trade_data)]])

def main():
    trade_data = get_ibkr_data('AAPL', '', '2000 S', '5 secs')

    last_price = trade_data['Average'][-1]
    mean_price = mean_reversion_price(trade_data['Average'])
    mom_price = momentum_price(trade_data['Average'])

    print("Last 5 prices: ", trade_data['Average'][-5:])
    print("Mean Reversion Price: %.2f, return to mean : %.2f"%(mean_price, (mean_price - last_price)/last_price))
    print("Momentum Price: %.2f, return to momentum : %.2f"%(mom_price, (mom_price - last_price)/last_price))

    if mom_price > last_price * 1.05:
        app = IBOrder('AAPL', 'BUY', 'MKT', 0, 100)
        app.run_client()
    elif mom_price < last_price * 0.95:
        app = IBOrder('AAPL', 'SELL', 'MKT', 0, 100)
        app.run_client()

if __name__ == "__main__":
    main()