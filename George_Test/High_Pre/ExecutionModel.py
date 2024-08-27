from AlgorithmImports import *

class ImmediateExecutionModelWithConditions(ExecutionModel):
    '''Provides an implementation of IExecutionModel that immediately submits market orders to achieve the desired portfolio targets with additional sell conditions'''

    def __init__(self):
        '''Initializes a new instance of the ImmediateExecutionModel class'''
        self.targets_collection = PortfolioTargetCollection()
        self.insight_timestamps = {}
        self.entry_prices = {}
        self.cooldown_periods = {}
        self.cooldown_duration = timedelta(minutes=60)

    def Execute(self, algorithm, targets):
        '''Immediately submits orders for the specified portfolio targets.
        Args:
            algorithm: The algorithm instance
            targets: The portfolio targets to be ordered'''

        current_time = algorithm.Time

        # Ensure trading is only done between 9:35 AM and 3:00 PM
        if current_time.time() < time(9, 35) or current_time.time() >= time(15, 0):
            return

        self.targets_collection.AddRange(targets)

        # Process each target
        for target in self.targets_collection.OrderByMarginImpact(algorithm):
            security = algorithm.Securities[target.Symbol]
            quantity = OrderSizing.GetUnorderedQuantity(algorithm, target, security)
            if quantity != 0:
                # Check if the symbol is in the cooldown period
                if target.Symbol in self.cooldown_periods and current_time < self.cooldown_periods[target.Symbol] + self.cooldown_duration:
                    algorithm.Debug(f"Skipping {target.Symbol} due to cooldown period")
                    continue

                above_minimum_portfolio = BuyingPowerModelExtensions.AboveMinimumOrderMarginPortfolioPercentage(
                    security.BuyingPowerModel,
                    security,
                    quantity,
                    algorithm.Portfolio,
                    algorithm.Settings.MinimumOrderMarginPortfolioPercentage)
                if above_minimum_portfolio:
                    algorithm.MarketOrder(security.Symbol, quantity)
                    self.insight_timestamps[target.Symbol] = current_time
                    self.entry_prices[target.Symbol] = security.Price
                elif not PortfolioTarget.MinimumOrderMarginPercentageWarningSent:
                    PortfolioTarget.MinimumOrderMarginPercentageWarningSent = False

        # Check for sell conditions and exit positions
        self.CheckSellConditions(algorithm, current_time)

        # Clear fulfilled targets
        self.targets_collection.ClearFulfilled(algorithm)

    def CheckSellConditions(self, algorithm, current_time):
        '''Check for sell conditions and exit positions'''
        sell_symbols = []

        for symbol, timestamp in self.insight_timestamps.items():
            security = algorithm.Securities[symbol]
            entry_price = self.entry_prices[symbol]
            current_price = security.Price

            # Calculate percentage change
            if entry_price == 0:  # Avoid division by zero
                continue
            percent_change = ((current_price - entry_price) / entry_price) * 100

            # Check if the position should be exited
            if percent_change <= -5 or percent_change >= 20 or current_time - timestamp >= timedelta(minutes = 15):
                sell_symbols.append(symbol)

        for symbol in sell_symbols:
            algorithm.Debug(f"Exiting position for {symbol} based on sell conditions")
            algorithm.Liquidate(symbol)
            del self.insight_timestamps[symbol]
            del self.entry_prices[symbol]
            self.cooldown_periods[symbol] = current_time  # Start cooldown period after exit