import pandas as pd
from datetime import datetime

class BalancedPortfolio():
    def __init__(self, initial_funds: dict, return_series: dict, start_date: datetime):
        """
        The constructor for BalancedPortfolio class.

        Parameters:
            initial_funds (dict): Initial funds distribution for each ticker.
            return_series (dict): Dictionary where each key is a ticker and value is a pandas Series of returns.
            start_date (datetime): Starting date of the investment.
        """
        self.funds = initial_funds
        self.return_series = return_series
        self.start_date = start_date
        self.current_date = start_date
        self.allocations = {ticker: 0.0 for ticker in initial_funds}  # Initialize allocations to 0% for each ticker

    def allocate(self, allocations):
        """
        Allocates the portfolio among various tickers.

        Parameters:
            allocations (dict): A dictionary of allocations for each ticker.

        Raises:
            ValueError: If the total allocation exceeds 100%.
        """
        if sum(allocations.values()) > 100:
            raise ValueError("Total allocation exceeds 100%")
        
        self.allocations = allocations

    def rebalance(self):
        """
        Rebalances the portfolio to maintain the allocation ratios.
        This is typically called after the market values have changed.
        """
        total_value = self.get_total_value()
        for ticker in self.funds:
            self.funds[ticker] = total_value * self.allocations.get(ticker, 0) / 100

    def update_date(self, new_date):
        """
        Updates the current date of the portfolio.

        Parameters:
            new_date (datetime): The new current date for the portfolio.
        """
        self.current_date = new_date

    def get_total_value(self):
        """
        Calculates the total value of the portfolio for all tickers.

        Returns:
            float: The total value of the portfolio.
        """
        total_value = 0
        for ticker, returns in self.return_series.items():
            # Localize the time zones of the return series to None for consistency
            if returns.index.tz is not None:
                returns.index = returns.index.tz_localize(None)

            # Select the right return value from the series up to the current date
            current_growth = returns.loc[:self.current_date].iloc[-1] if not returns.empty else 0
            total_value += self.funds.get(ticker, 0) * (1 + current_growth)
        return total_value + self.funds['cash']

    def __str__(self):
        """
        String representation of the BalancedPortfolio object.

        Returns:
            str: A string showing the portfolio allocation and total value.
        """
        allocation_str = ', '.join([f"{ticker}: {alloc}%" for ticker, alloc in self.allocations.items()])
        return f"Portfolio Allocation: {allocation_str}, Total Value: {self.get_total_value():.2f}"

def calculate_returns(hist_data, adjclose=True):
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
