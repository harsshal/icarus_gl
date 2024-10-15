from sklearn.linear_model import LinearRegression
import numpy as np

def mean_reversion_price(trade_data):
    return sum(trade_data) / len(trade_data)

def momentum_price(trade_data):
    # using linear regression

    X = np.array(range(len(trade_data))).reshape(-1, 1)
    y = trade_data
    model = LinearRegression().fit(X, y)
    return model.predict([[len(trade_data)]])