from AlgorithmImports import *
import numpy as np
from sklearn.linear_model import LinearRegression

class SlopeRiskModel(RiskManagementModel):
    '''Custom risk management model that manages risk based on the slope of past prices.'''

    def __init__(self, slope_threshold=1, window_size=20):
        '''Initializes a new instance of the CustomSlopeRiskModel class
        Args:
            slope_threshold: The slope threshold for risk management, defaults to -0.5
            window_size: The number of seconds to calculate the slope over, defaults to 20
        '''
        self.slope_threshold = slope_threshold
        self.window_size = window_size
        self.past_prices = RollingWindow[TradeBar](window_size)

    def ManageRisk(self, algorithm, targets):
        '''Manages the algorithm's risk at each time step
        Args:
            algorithm: The algorithm instance
            targets: The current portfolio targets to be assessed for risk
        '''
        risk_adjusted_targets = []

        for kvp in algorithm.Portfolio:
            symbol = kvp.Key
            position = kvp.Value

            # Get the past prices
            past_prices = [x.Close for x in self.past_prices if x is not None]
            slope = self.compute_slope(past_prices)

            # Get the current price
            current_price = algorithm.Securities[symbol].Price

            # Check if the slope is less than the threshold
            if slope < self.slope_threshold:
                algorithm.insights.cancel([ symbol ]);
                # Reduce position size or close position
                risk_adjusted_targets.append(PortfolioTarget(symbol, 0))

        return risk_adjusted_targets

    def compute_slope(self, prices: list) -> float:
        if len(prices) < 2:
            return 0.0
        
        # Convert list to numpy array and reshape to 2D for sklearn
        prices_array = np.array(prices).reshape(-1, 1)

        # Create an array of indices representing time
        times = np.array(range(len(prices))).reshape(-1, 1)

        # Fit a linear regression model
        model = LinearRegression().fit(times, prices_array)

        # Return the slope of the regression line
        return model.coef_[0][0]