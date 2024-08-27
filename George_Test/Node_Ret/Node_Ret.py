# region imports
from AlgorithmImports import *
from datetime import timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
# endregion

class VolumeProfileAlgorithm(QCAlgorithm):
    def initialize(self):
        self.set_start_date(2024, 8, 1)
        self.set_end_date(2024, 8, 26)
        self.set_cash(100000)
        self.symbols = [self.add_equity(symbol, Resolution.Minute).symbol for symbol in self.get_sp500_symbols()]
        
        # Volume Profile indicator settings
        self.profile_period = 120  # 2 hours
        self.value_area_percentage = 0.7
        
        # Initialize dictionaries to store indicators and rolling windows for each symbol
        self.volume_profiles = {}
        self.past_prices = {}
        self.past_prices_slow = {}
        self.stop_loss_indicators = {}
        self.stop_loss_prices = {}
        
        for symbol in self.symbols:
            self.volume_profiles[symbol] = VolumeProfile("Volume Profile", self.profile_period, self.value_area_percentage)
            self.past_prices[symbol] = RollingWindow[TradeBar](20)
            self.past_prices_slow[symbol] = RollingWindow[TradeBar](100)
            self.stop_loss_indicators[symbol] = self.MIN(symbol, 100, Resolution.Minute)
            self.stop_loss_prices[symbol] = 0
        
            # Consolidate data and register indicators for each symbol
            self.consolidate(symbol, timedelta(minutes=1), self.on_data_consolidated)
            self.register_indicator(symbol, self.volume_profiles[symbol], timedelta(hours=2))
        
        # Warm up using historical data
        for symbol in self.symbols:
            history = self.history[TradeBar](symbol, timedelta(days=1), Resolution.Minute)
            for trade_bar in history:
                self.volume_profiles[symbol].update(trade_bar)
                self.stop_loss_indicators[symbol].update(trade_bar.end_time, trade_bar.close)
                self.past_prices[symbol].add(trade_bar)
                self.past_prices_slow[symbol].add(trade_bar)

        
        self.log("Finished warming up indicators")

    def get_sp500_symbols(self):
        sp500 = ["SPY",  # Apple Inc.
        ]
        return sp500

    def on_data_consolidated(self, trade_bar: TradeBar):
        if trade_bar.symbol in self.past_prices:
            self.past_prices[trade_bar.symbol].add(trade_bar)
            self.past_prices_slow[trade_bar.symbol].add(trade_bar)

    def on_data(self, data: Slice):
        for symbol in self.symbols:
            if symbol not in data:
                continue

            # Check if the strategy warm-up period is over and indicators are ready
            if not self.volume_profiles[symbol].is_ready or not self.past_prices[symbol].is_ready or not self.stop_loss_indicators[symbol].is_ready:
                continue

            current_price = self.past_prices[symbol][0].close
            past_prices = [x.close for x in self.past_prices[symbol] if x is not None]
            past_prices_slow = [x.close for x in self.past_prices_slow[symbol] if x is not None]

            # Verify entry criteria to invest
            if not self.portfolio[symbol].invested:
                # Check if price is moving towards the value area based on the direction of the slope
                # and the volume profile
                past_prices = [x.close for x in self.past_prices[symbol] if x is not None]
                past_prices_slow = [x.close for x in self.past_prices_slow[symbol] if x is not None]
                slope = self.compute_slope(past_prices)
                slope_slow = self.compute_slope(past_prices_slow)
                

                # Log the indicators and price
                self.log(f"Current Price: {current_price} and Slope: {slope} for {symbol}")
                self.log(f"Value Area High: {self.volume_profiles[symbol].value_area_high} for {symbol}")
                self.log(f"Value Area Low: {self.volume_profiles[symbol].value_area_low} for {symbol}")

                if (self.volume_profiles[symbol].value_area_low <= current_price <= self.volume_profiles[symbol].value_area_high):
                    # Long condition
                    if slope < -0.000000 and slope_slow > 0:
                        self.log(f"Price is moving towards the value area! Invest in {symbol}!")
                        self.set_holdings(symbol, 1)  
                        self.stop_loss_prices[symbol] = self.stop_loss_indicators[symbol].current.value
                        self.log(f"Current price: {current_price}, stop order price: {self.stop_loss_prices[symbol]} for {symbol}")
                    else:
                        self.log(f"Price isn't in value area, keep waiting for {symbol}...")

            # Exit or update exit stop loss price
            else:
                # Exit check
                if current_price < self.stop_loss_prices[symbol] or current_price < self.volume_profiles[symbol].value_area_low:
                    self.log(f"Stop loss at {current_price} for {symbol}")
                    self.liquidate(symbol)
                # Check if you should update stop loss price
                elif self.past_prices[symbol][0].close > self.past_prices[symbol][1].close:
                    self.stop_loss_prices[symbol] = self.stop_loss_prices[symbol] + (self.past_prices[symbol][0].close - self.past_prices[symbol][1].close)
                    self.log(f"Updating stop loss order of {self.stop_loss_prices[symbol]} for {symbol}!")

    def compute_slope(self, prices: list) -> float:
        # Convert list to numpy array and reshape to 2D for sklearn
        prices_array = np.array(prices).reshape(-1, 1)

        # Create an array of indices representing time
        times = np.array(range(len(prices))).reshape(-1, 1)

        # Fit a linear regression model
        model = LinearRegression().fit(times, prices_array)

        # Return the slope of the regression line
        return model.coef_[0][0]/prices_array[0]
