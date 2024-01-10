from ..base_portfolio import BasePortfolio
from datetime import datetime
import Constants.asset_classes as AC

class BalancedPortfolio(BasePortfolio):
    def __init__(self, initial_funds: dict, return_series: dict, start_date: datetime.date, end_date: datetime.date, rebalance_frequency: str, investment_vehicles: dict):
        super().__init__(initial_funds, return_series, start_date, end_date, rebalance_frequency)
        self.investment_vehicles = investment_vehicles  # Store the investment vehicles
        self.allocate_balanced()

    def allocate_balanced(self):
        # Define the allocation ratio for each investment vehicle
        asset_allocation_ratios = {AC.STOCK: 0.15,
                                   AC.BOND: 0.70,
                                   AC.CASH or AC.CASH_EQUIVALENT: 0.10,
                                   AC.COMMODITY: 0.05}

        # Calculate the actual allocation ratios based on available investment vehicles
        actual_ratios = {atype: ratio for atype, ratio in asset_allocation_ratios.items() if any(t == atype for t in self.investment_vehicles.values())}
        total_actual_ratio = sum(actual_ratios.values())

        # Adjust the allocation ratios to sum up to 100%
        adjusted_ratios = {atype: (ratio / total_actual_ratio) * 100 for atype, ratio in actual_ratios.items()}

        balanced_allocations = {}
        for ticker, ticker_investment_vehicle in self.investment_vehicles.items():
            if ticker_investment_vehicle in adjusted_ratios:
                # Count how many tickers are there for each investment vehicle
                num_tickers = sum(1 for t in self.investment_vehicles.values() if t == ticker_investment_vehicle)
                
                # Distribute the allocation for this investment vehicle evenly among its tickers
                balanced_allocations[ticker] = (adjusted_ratios[ticker_investment_vehicle] / num_tickers)

        self.allocate(balanced_allocations)
