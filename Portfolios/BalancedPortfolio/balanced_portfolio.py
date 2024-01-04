import pandas as pd
from datetime import datetime

class BalancedPortfolio():
    """
    A class to represent a balanced investment portfolio.

    Attributes:
        funds (dict): A dictionary with the initial funds allocated to stocks, bonds, and cash.
        stock_returns (pd.Series): A pandas Series containing stock returns.
        bond_returns (pd.Series): A pandas Series containing bond returns.
        start_date (datetime): The starting date of the investment.
        current_date (datetime): The current date for calculating the portfolio's value.
        stocks (float): The percentage of the portfolio allocated to stocks.
        bonds (float): The percentage of the portfolio allocated to bonds.
        cash (float): The percentage of the portfolio held in cash.
    """

    def __init__(self, initial_funds: dict, stock_returns: pd.Series, bond_returns: pd.Series, start_date: datetime):
        """
        The constructor for BalancedPortfolio class.

        Parameters:
            initial_funds (dict): Initial funds distribution.
            stock_returns (pd.Series): Series of stock returns.
            bond_returns (pd.Series): Series of bond returns.
            start_date (datetime): Starting date of the investment.
        """
        self.funds = initial_funds
        self.stock_returns = stock_returns
        self.bond_returns = bond_returns
        self.start_date = start_date
        self.current_date = start_date
        self.stocks = 0.0
        self.bonds = 0.0
        self.cash = 100.0  # Initially, 100% of the portfolio is in cash

    def allocate(self, stocks_percent, bonds_percent):
        """
        Allocates the portfolio among stocks, bonds, and cash.

        Parameters:
            stocks_percent (float): The percentage of the portfolio to allocate to stocks.
            bonds_percent (float): The percentage of the portfolio to allocate to bonds.

        Raises:
            ValueError: If the total allocation exceeds 100%.
        """
        if stocks_percent + bonds_percent > 100:
            raise ValueError("Total allocation exceeds 100%")
        self.stocks = stocks_percent
        self.bonds = bonds_percent
        self.cash = 100 - stocks_percent - bonds_percent  # Remaining percentage is allocated to cash

    def rebalance(self):
        """
        Rebalances the portfolio to maintain the allocation ratios.
        This is typically called after the market values have changed.
        """
        total_value = self.get_total_value()
        self.funds['stocks'] = total_value * self.stocks / 100
        self.funds['bonds'] = total_value * self.bonds / 100
        self.funds['cash'] = total_value * self.cash / 100

    def update_date(self, new_date):
        """
        Updates the current date of the portfolio.

        Parameters:
            new_date (datetime): The new current date for the portfolio.
        """
        self.current_date = new_date

    def get_total_value(self):
        """
        Calculates the total value of the portfolio including stocks, bonds, and cash.

        Returns:
            float: The total value of the portfolio.
        """
        # Localize the time zones of the return series to None for consistency
        if self.stock_returns.index.tz is not None:
            self.stock_returns.index = self.stock_returns.index.tz_localize(None)
        if self.bond_returns.index.tz is not None:
            self.bond_returns.index = self.bond_returns.index.tz_localize(None)

        # Select the right return value from the series up to the current date
        current_stock_growth = self.stock_returns.loc[:self.current_date].iloc[-1]
        current_bond_growth = self.bond_returns.loc[:self.current_date].iloc[-1]

        # Calculate the current value of stocks and bonds in the portfolio
        current_stocks_value = self.funds['stocks'] * (1 + current_stock_growth)
        current_bonds_value = self.funds['bonds'] * (1 + current_bond_growth)
        return current_stocks_value + current_bonds_value + self.funds['cash']

    def __str__(self):
        """
        String representation of the BalancedPortfolio object.

        Returns:
            str: A string showing the portfolio allocation and total value.
        """
        return f"Portfolio Allocation: {self.stocks}% Stocks, {self.bonds}% Bonds, {self.cash}% Cash, Total Value: {self.get_total_value():.2f}"

def calculate_returns(hist_data, adjclose=False):
    """
    Calculates various types of returns for a given historical data.

    Parameters:
        hist_data (DataFrame): The historical data of a financial instrument.
        adjclose (bool): A flag to determine if adjusted close prices should be used.

    Returns:
        dict: A dictionary containing full, annualized, quarterly, monthly, weekly, and daily returns.
    """
    # Ensure the data is sorted by date
    hist_data = hist_data.sort_index()

    # Choose between adjusted close prices or raw close prices
    if adjclose:
        # Adjust for dividends
        total_return_data = hist_data['adjclose']
    else:
        # Only consider price changes
        total_return_data = hist_data['close']

    # Calculate full return from start to end
    start_value = total_return_data.iloc[0]
    end_value = total_return_data.iloc[-1]
    full_return = (end_value / start_value) - 1
    full_return_series = pd.Series([full_return], index=[hist_data.index[-1]])

    # Calculate other types of returns
    annualized_return = total_return_data.resample('Y').ffill().pct_change()
    quarterly_returns = total_return_data.resample('Q').ffill().pct_change()
    monthly_returns = total_return_data.resample('M').ffill().pct_change()
    weekly_returns = total_return_data.resample('W').ffill().pct_change()
    daily_returns = total_return_data.pct_change()

    # Return a dictionary containing all the calculated returns
    return {
        'full_return': full_return_series,
        'annualized_return': annualized_return,
        'quarterly_returns': quarterly_returns,
        'monthly_returns': monthly_returns,
        'weekly_returns': weekly_returns,
        'daily_returns': daily_returns
    }
