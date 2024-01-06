from ..base_portfolio import BasePortfolio
from datetime import datetime
import Constants.investment_vehicles as IV

class BalancedPortfolio(BasePortfolio):
    def __init__(self, initial_funds: dict, return_series: dict, start_date: datetime.date, asset_types: dict):
        super().__init__(initial_funds, return_series, start_date)
        self.asset_types = asset_types  # Store the asset types
        self.allocate_balanced()

    def allocate_balanced(self):
        # Define the allocation ratio for each asset type
        asset_allocation_ratios = {IV.STOCK: 0.55,
                                   IV.BOND: 0.35,
                                   IV.CASH or IV.CASH_EQUIVALENT: 0.05,
                                   IV.COMODITY: 0.05}

        # Calculate the actual allocation ratios based on available asset types
        actual_ratios = {atype: ratio for atype, ratio in asset_allocation_ratios.items() if any(t == atype for t in self.asset_types.values())}
        total_actual_ratio = sum(actual_ratios.values())

        # Adjust the allocation ratios to sum up to 100%
        adjusted_ratios = {atype: (ratio / total_actual_ratio) * 100 for atype, ratio in actual_ratios.items()}

        balanced_allocations = {}
        for ticker, ticker_asset_type in self.asset_types.items():
            if ticker_asset_type in adjusted_ratios:
                # Count how many tickers are there for each asset type
                num_tickers = sum(1 for t in self.asset_types.values() if t == ticker_asset_type)
                
                # Distribute the allocation for this asset type evenly among its tickers
                balanced_allocations[ticker] = (adjusted_ratios[ticker_asset_type] / num_tickers)

        self.allocate(balanced_allocations)
