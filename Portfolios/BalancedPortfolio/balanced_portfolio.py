import pandas as pd
from datetime import datetime

class BalancedPortfolio():
    def __init__(self, initial_funds: dict, stock_returns: pd.Series, bond_returns: pd.Series, start_date: datetime):
        self.funds = initial_funds
        self.stock_returns = stock_returns
        self.bond_returns = bond_returns
        self.start_date = start_date
        self.current_date = start_date
        self.stocks = 0.0
        self.bonds = 0.0
        self.cash = 100.0

    def allocate(self, stocks_percent, bonds_percent):
        if stocks_percent + bonds_percent > 100:
            raise ValueError("Total allocation exceeds 100%")
        self.stocks = stocks_percent
        self.bonds = bonds_percent
        self.cash = 100 - stocks_percent - bonds_percent

    def rebalance(self):
        total_value = self.get_total_value()
        self.funds['stocks'] = total_value * self.stocks / 100
        self.funds['bonds'] = total_value * self.bonds / 100
        self.funds['cash'] = total_value * self.cash / 100

    def update_date(self, new_date):
        self.current_date = new_date

    def get_total_value(self):

        if self.stock_returns.index.tz is not None:
            self.stock_returns.index = self.stock_returns.index.tz_localize(None)
        if self.bond_returns.index.tz is not None:
            self.bond_returns.index = self.bond_returns.index.tz_localize(None)

        # Use returns series to calculate current value
        # This part will require logic to select the right return value from the series
        current_stock_growth = self.stock_returns.loc[:self.current_date].iloc[-1]
        current_bond_growth = self.bond_returns.loc[:self.current_date].iloc[-1]

        current_stocks_value = self.funds['stocks'] * (1 + current_stock_growth)
        current_bonds_value = self.funds['bonds'] * (1 + current_bond_growth)
        return current_stocks_value + current_bonds_value + self.funds['cash']

    def __str__(self):
        return f"Portfolio Allocation: {self.stocks}% Stocks, {self.bonds}% Bonds, {self.cash}% Cash, Total Value: {self.get_total_value():.2f}"


def calculate_returns(hist_data):
    # Ensure the data is sorted by date
    hist_data = hist_data.sort_index()

    # Full Return
    start_price = hist_data['close'].iloc[0]
    end_price = hist_data['close'].iloc[-1]
    full_return = (end_price / start_price) - 1
    # Creating a single-value Series for full return
    full_return_series = pd.Series([full_return], index=[hist_data.index[-1]])

    # Annualized Return
    annualized_return = hist_data['close'].resample('Y').ffill().pct_change()

    # Quarterly Return
    quarterly_returns = hist_data['close'].resample('Q').ffill().pct_change()

    # Monthly Return
    monthly_returns = hist_data['close'].resample('M').ffill().pct_change()

    # Weekly Return
    weekly_returns = hist_data['close'].resample('W').ffill().pct_change()

    # Daily Return
    daily_returns = hist_data['close'].pct_change()

    return {
        'full_return': full_return_series,
        'annualized_return': annualized_return,
        'quarterly_returns': quarterly_returns,
        'monthly_returns': monthly_returns,
        'weekly_returns': weekly_returns,
        'daily_returns': daily_returns
    }

