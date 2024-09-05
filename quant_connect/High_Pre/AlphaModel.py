from AlgorithmImports import *

class HighVolumeAlphaModel(AlphaModel):
    '''Alpha model that generates insights based on extreme high volume in the previous 10-second bar.'''

    def __init__(self):
        self.symbol_data_by_symbol = {}
        self.opening_prices = {}
        

    def Update(self, algorithm, data):
        insights = []
        current_time = algorithm.Time

        if current_time.time() < time(9, 35) or current_time.time() >= time(16, 0):
            return []
        if not (algorithm.IsMarketOpen(sym) for sym, _ in self.symbol_data_by_symbol.items()):
            return []
        for symbol, symbol_data in self.symbol_data_by_symbol.items():
            if not symbol_data.CanEmit:
                continue

            if symbol not in self.opening_prices:
                self.opening_prices[symbol] = algorithm.Securities[symbol].Open

            open_price = self.opening_prices[symbol]
            current_price = symbol_data.CurrentPrice

            if open_price == 0:  # Avoid division by zero
                continue

            percent_change = ((current_price - open_price) / open_price) * 100

            # Only consider stocks that are up by at least 5% since open
            #if percent_change < 0:
                #continue
        
            # Calculate the volume ratio and scale it to the range [-1, 1]
            volume_ratio = symbol_data.CurrentVolume / symbol_data.VolumeStdDev
            #scaled_volume_ratio = max(min(volume_ratio, 1), -1)  # Ensure the ratio is within the range [-1, 1]

            direction = InsightDirection.FLAT
            direction = InsightDirection.FLAT
            if symbol_data.CurrentPrice > symbol_data.PreviousPrice:
                direction = InsightDirection.UP
            if direction == InsightDirection.UP and abs(volume_ratio) > 0.5:
                insights.append(Insight.Price(symbol, timedelta(minutes = 60), direction, weight=abs(volume_ratio)))

        return insights

    def OnSecuritiesChanged(self, algorithm, changes):
        for removed in changes.RemovedSecurities:
            symbol_data = self.symbol_data_by_symbol.pop(removed.Symbol, None)
            if symbol_data is not None:
                symbol_data.RemoveConsolidators(algorithm)

        for added in changes.AddedSecurities:
            if added.Symbol not in self.symbol_data_by_symbol:
                symbol_data = SymbolData(added.Symbol, algorithm)
                self.symbol_data_by_symbol[added.Symbol] = symbol_data

class SymbolData:
    '''Contains data specific to a symbol required by this model'''
    def __init__(self, symbol, algorithm):
        self.symbol = symbol
        self.algorithm = algorithm

        # Initialize RollingWindow for 6 months of daily volumes (approx. 126 trading days)
        self.daily_volume = RollingWindow[float](126)
        self.volume_std_dev = 0

        self.consolidator = TradeBarConsolidator(timedelta(seconds=60))
        self.consolidator.DataConsolidated += self.OnDataConsolidated

        self.algorithm.SubscriptionManager.AddConsolidator(self.symbol, self.consolidator)

        history = algorithm.history(self.symbol, 126, Resolution.Daily)
        for bar in history.itertuples():
            self.daily_volume.add(bar.volume)

        if self.daily_volume.IsReady:
            self.volume_std_dev = self.CalculateVolumeStdDev()

        self.current_volume = 0
        self.current_price = 0
        self.previous_price = 0

    def OnDataConsolidated(self, sender, bar):
        self.current_volume = bar.Volume
        self.previous_price = self.current_price
        self.current_price = bar.Close

    def CalculateVolumeStdDev(self):
        volumes = [v for v in self.daily_volume]
        return np.std(volumes)

    @property
    def VolumeStdDev(self):
        return self.volume_std_dev

    @property
    def CurrentVolume(self):
        return self.current_volume

    @property
    def CurrentPrice(self):
        return self.current_price

    @property
    def PreviousPrice(self):
        return self.previous_price

    @property
    def CanEmit(self):
        return self.daily_volume.IsReady

    def RemoveConsolidators(self, algorithm):
        algorithm.SubscriptionManager.RemoveConsolidator(self.symbol, self.consolidator)