# region imports
from AlgorithmImports import *
from datetime import timedelta
import numpy as np
from sklearn.linear_model import LinearRegression


# endregion

class VolumeProfileAlgorithm(QCAlgorithm):
    def initialize(self):
        self.set_start_date(2024, 1, 1)
        self.set_end_date(2024, 7, 21)  # Corrected end date
        self.set_cash(100000)

        # Set the symbol of the asset we want to trade
        self.equity = self.add_equity("TSLA", Resolution.MINUTE)
        self.symbol = self.equity.symbol

        # Volume Profile indicator settings
        self.profile_period = 120  # 2 hours
        self.value_area_percentage = 0.4
        self.volume_profile = VolumeProfile("Volume Profile", self.profile_period, self.value_area_percentage)

        # Rolling window to store past prices
        self.past_prices_period = 20
        self.past_prices = RollingWindow[TradeBar](self.past_prices_period)

        # Rolling window to store past 120 minutes prices
        self.past_120_prices_period = 120
        self.past_120_minutes_prices = RollingWindow[TradeBar](self.past_120_prices_period)

        # Consolidate data
        self.consolidate(self.symbol, timedelta(minutes=1), self.on_data_consolidated)
        self.register_indicator(self.symbol, self.volume_profile, timedelta(hours=2))

        # Setting stoploss
        self.stop_loss_len = 20
        self.stop_loss_indicator = self.min(self.symbol, self.stop_loss_len, Resolution.MINUTE)
        self.stop_loss_price = 0

        # Warm up using historical method
        history = self.history[TradeBar](self.symbol, timedelta(days=1), Resolution.MINUTE)
        for trade_bar in history:
            self.volume_profile.update(trade_bar)
            self.stop_loss_indicator.update(trade_bar.end_time, trade_bar.close)
            self.past_prices.add(trade_bar)
            self.past_120_minutes_prices.add(trade_bar)
        self.log("Finished warming up indicator")

        # Free portfolio setting
        self.settings.free_portfolio_value = 0.3

    def on_data_consolidated(self, trade_bar: TradeBar):
        # Store the past prices of the equity
        self.past_prices.add(trade_bar)
        self.past_120_minutes_prices.add(trade_bar)

    def on_data(self, data: Slice):
        # Check if the strategy warm up period is over and indicators are ready
        if self.is_warming_up or not self.volume_profile.is_ready or not self.past_prices.is_ready or not self.stop_loss_indicator.is_ready or not self.past_120_minutes_prices.is_ready:
            return

        current_price = self.past_prices[0].close

        # Verify entry criteria to invest
        if not self.portfolio.invested:
            self.log("Not invested! Finding equity contract...")

            # Check if price is moving towards the value area based on the direction of the slope and the volume profile
            past_prices = [x.close for x in self.past_prices if x is not None]
            slope = self.compute_slope(past_prices)

            # Compute the slope of the past 120 minutes prices
            past_120_prices = [x.close for x in self.past_120_minutes_prices if x is not None]
            slope_120 = self.compute_slope(past_120_prices)

            # Log the indicators and price
            self.log(f"Current Price: {current_price}, Slope: {slope}, 120-Minute Slope: {slope_120}")
            self.log(f"Value Area High: {self.volume_profile.value_area_high}")
            self.log(f"Value Area Low: {self.volume_profile.value_area_low}")

            if (
                    self.volume_profile.value_area_low <= current_price <= self.volume_profile.value_area_high) and slope_120 > 0:
                # Long condition
                if slope < -0.0005 and slope_120 > 0.0003:
                    self.log("Price is moving towards the value area! Invest!")
                    self.set_holdings(self.symbol, 1)
                    self.stop_loss_price = self.stop_loss_indicator.current.value
                    self.log(f"Current price: {current_price}, stop order price: {self.stop_loss_price}")
                else:
                    self.log("Price isn't in value area, keep waiting...")

        # Exit or update exit stop loss price
        else:
            # Exit check
            if current_price < self.stop_loss_price:
                self.log(f"Stop loss at {current_price}")
                self.liquidate(self.symbol)
            # Check if you should update stop loss price
            elif self.past_prices[0].close > self.past_prices[1].close:
                self.stop_loss_price = self.stop_loss_price + (self.past_prices[0].close - self.past_prices[1].close)
                self.log(f"Updating stop loss order of {self.stop_loss_price}!")

    def compute_slope(self, prices: list) -> float:
        # Convert list to numpy array and reshape to 2D for sklearn
        prices_array = np.array(prices).reshape(-1, 1)

        # Create an array of indices representing time
        times = np.array(range(len(prices))).reshape(-1, 1)

        # Fit a linear regression model
        model = LinearRegression().fit(times, prices_array)

        # Return the slope of the regression line
        return model.coef_[0][0]
