# region imports
from AlgorithmImports import *
from AlphaModel import *
from PortfolioModel import *
from ExecutionModel import *
from RiskModel import *
# endregion

class AlertRedOrangeRhinoceros(QCAlgorithm):

    def Initialize(self):
        self.set_start_date(2024, 5, 15)
        self.set_end_date(2024, 7, 16)
        self.set_cash(100000)
        self.set_brokerage_model(BrokerageName.InteractiveBrokersBrokerage)
        self._rebalance_time = datetime(2024, 7, 15) # Initialize with a very early time

        # Schedule rebalancing event at 4 AM every trading day
        self.schedule.on(self.date_rules.every_day(), self.time_rules.at(4, 0), self.Rebalance)
        
        self._num_coarse = 5000
        self.universe_settings.resolution = Resolution.SECOND
        self.add_universe(self.CoarseSelectionFunction)

        self.add_alpha(HighVolumeAlphaModel())

        self.set_portfolio_construction((FixedDollarAmountPortfolioConstructionModel(Resolution.DAILY)))

        self.set_risk_management(SlopeRiskModel())

        self.set_execution(ImmediateExecutionModelWithConditions())

    def IsRebalanceDue(self, time):
        return True

    def Rebalance(self):
        self._rebalance_time = self.Time
        self.Debug(f"Rebalancing at {self.Time}")

    def CoarseSelectionFunction(self, coarse):
        if not self.IsRebalanceDue(self.Time):
            return Universe.Unchanged

        selected = sorted([x for x in coarse if x.Price < 5 and x.Volume > 1000000],
                          key=lambda x: x.DollarVolume, 
                          reverse=True)

        return [x.Symbol for x in selected[:self._num_coarse]]