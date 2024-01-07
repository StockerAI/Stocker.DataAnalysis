import pandas
import numpy
import datetime
from dateutil.relativedelta import relativedelta
import Constants.rebalance_date_options as RDO

class BasePortfolio():
    def __init__(self, initial_funds: dict, return_series: dict, start_date: datetime.date):
        """
        The constructor for BasePortfolio class.

        Parameters:
            initial_funds (dict): Initial funds distribution for each ticker.
            return_series (dict): Dictionary where each key is a ticker and value is a pandas Series of returns.
            start_date (datetime.date): Starting date of the investment.
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
            new_date (datetime.date): The new current date for the portfolio.
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
            # Select the right return value from the series up to the current date
            current_growth = returns["full_return"].loc[:self.current_date].iloc[-1] if not returns["full_return"].empty else 0
            total_value += self.funds.get(ticker, 0) * (1 + current_growth)
        return total_value + self.funds["cash"]
    
    def get_return_percentage(self):
        """
        Calculates the return of the portfolio as a percentage.

        Returns:
            float: The return percentage of the portfolio.
        """
        initial_value = sum(self.funds.values())
        current_value = self.get_total_value()
        return ((current_value - initial_value) / initial_value) * 100

    def get_cagr(self):
            """
            Calculates the Compound Annual Growth Rate (CAGR) of the portfolio.

            Returns:
                float: The CAGR of the portfolio.
            """
            starting_value = sum(self.funds.values())
            ending_value = self.get_total_value()
            total_years = (self.current_date - self.start_date).days / 365.25

            if starting_value <= 0 or total_years <= 0:
                return 0  # Avoid division by zero or negative values

            return ((ending_value / starting_value) ** (1 / total_years) - 1) * 100

    def get_stdev_percentage(self):
        """
        Calculates the standard deviation of the portfolio's daily returns as a percentage.

        Returns:
            float: The standard deviation of the daily returns.
        """
        all_daily_returns = list()

        # Aggregate daily returns from each ticker
        for _, returns_dict in self.return_series.items():
            # Extract daily returns for this ticker
            daily_returns = returns_dict.get("monthly_returns", []).dropna()
            
            # Append to the list of all daily returns
            all_daily_returns.extend(daily_returns)

        # Calculate and return the standard deviation
        return numpy.std(all_daily_returns, ddof=1) * 100  # Using ddof=1 for sample standard deviation
    
    def get_max_drawdown_percentage(self):
        """
        Calculates the maximum drawdown of the portfolio as a percentage.

        Returns:
            float: The maximum drawdown percentage of the portfolio.
        """
        cumulative_returns = 0
        for ticker, returns_dict in self.return_series.items():
            # Get monthly returns up to the current date
            monthly_returns = returns_dict["monthly_returns"].loc[:self.current_date]
            
            # Calculate cumulative returns for this ticker
            cumulative_returns += (1 + monthly_returns).cumprod() * self.funds.get(ticker, 0)

        # Calculate drawdowns
        peak = cumulative_returns.cummax()
        drawdowns = (cumulative_returns - peak) / peak

        # Max drawdown
        max_drawdown = drawdowns.min()  # Since drawdowns are negative, min() gives the max drawdown
        return abs(max_drawdown) * 100

    # def get_sharpe_ratio(self, risk_free_rate):
    #     """
    #     Calculates the Sharpe Ratio of the portfolio.

    #     Parameters:
    #         risk_free_rate (float): The risk-free rate.

    #     Returns:
    #         float: The Sharpe Ratio of the portfolio.
    #     """
    #     portfolio_return = self.get_return_percentage() / 100
    #     stdev = self.get_stdev_percentage() / 100
    #     return (portfolio_return - risk_free_rate) / stdev

    # def get_sortino_ratio(self, risk_free_rate):
    #     """
    #     Calculates the Sortino Ratio of the portfolio.

    #     Parameters:
    #         risk_free_rate (float): The risk-free rate.

    #     Returns:
    #         float: The Sortino Ratio of the portfolio.
    #     """
    #     portfolio_return = self.get_return_percentage() / 100
    #     negative_returns = [return_ for return_ in self.get_daily_returns() if return_ < 0]
    #     downside_deviation = numpy.std(negative_returns)
    #     return (portfolio_return - risk_free_rate) / downside_deviation

    def __str__(self):
        """
        String representation of the BasePortfolio object.

        Returns:
            str: A string showing the portfolio allocation and total value.
        """
        allocation_str = ", ".join([f"{ticker}: {alloc}%" for ticker, alloc in self.allocations.items()])
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
        total_return_data = hist_data["adjclose"]
    else:
        # Only consider price changes
        total_return_data = hist_data["close"]
    
    if not isinstance(hist_data.index, pandas.DatetimeIndex):
        total_return_data.index = pandas.to_datetime(total_return_data.index)

    # Calculate full return from start to end
    start_value = total_return_data.iloc[0]
    end_value = total_return_data.iloc[-1]
    full_return = (end_value / start_value) - 1
    full_return_series = pandas.Series([full_return], index=[hist_data.index[-1]])

    # Calculate other types of returns
    annualized_returns = total_return_data.resample("Y").ffill().pct_change()
    quarterly_returns = total_return_data.resample("Q").ffill().pct_change()
    monthly_returns = total_return_data.resample("M").ffill().pct_change()
    weekly_returns = total_return_data.resample("W").ffill().pct_change()
    daily_returns = total_return_data.pct_change()

    # Return a dictionary containing all the calculated returns
    return {
        "full_return": full_return_series,
        "annualized_returns": annualized_returns,
        "quarterly_returns": quarterly_returns,
        "monthly_returns": monthly_returns,
        "weekly_returns": weekly_returns,
        "daily_returns": daily_returns
    }

def generate_rebalance_dates(start_date, end_date, frequency=RDO.NEVER):
    if frequency == RDO.NEVER:
        return [end_date]  # Only the end date for "NEVER" frequency

    frequencies = {
        RDO.MONTHLY: relativedelta(months=+1),
        RDO.QUARTERLY: relativedelta(months=+3),
        RDO.SEMI_ANNUALLY: relativedelta(months=+6),
        RDO.ANNUALLY: relativedelta(years=+1)
    }
    delta = frequencies.get(frequency)
    dates = []
    current_date = start_date
    while current_date <= end_date:
        if delta:  # Adjust to get the last day of the month for all frequencies except "never"
            current_date = last_day_of_month(current_date)
        dates.append(current_date)
        if delta is None:  # Should not reach here for "never", but just as a safeguard
            break
        current_date += delta
    if end_date not in dates:
        dates.append(end_date)
    return dates

def last_day_of_month(any_day):
    """Return the last day of the month of any_day"""
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)