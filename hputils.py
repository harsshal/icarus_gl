import sys
import os
from sklearn.linear_model import LinearRegression
import numpy as np


def add_to_sys_path(path_str):
    # Get the parent directory and add it to sys.path
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), path_str))
    sys.path.insert(0, parent_dir)

add_to_sys_path('../ibapi')

def mean_reversion_price(trade_data):
    return sum(trade_data) / len(trade_data)

def momentum_price(trade_data):
    # using linear regression

    X = np.array(range(len(trade_data))).reshape(-1, 1)
    y = trade_data
    model = LinearRegression().fit(X, y)
    return model.predict([[len(trade_data)]])