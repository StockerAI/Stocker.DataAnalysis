import pandas
import numpy
import datetime
import collections
from dateutil.relativedelta import relativedelta
from Constants.rebalance_date_options import RDO

class BasePortfolio():
    def __init__(self, initial_funds: dict, return_series: dict, start_date: datetime.date, end_date: datetime.date, rebalance_frequency=RDO["NEVER"]):
        """
        The constructor for BasePortfolio class.

        Parameters:
            initial_funds (dict): Initial funds distribution for each ticker.
            return_series (dict): Dictionary where each key is a ticker and value is a pandas Series of returns.
            start_date (datetime.date): Starting date of the investment.
            end_date (datetime.date): Ending date of the investment.
            rebalance_frequency (str): Frequency of rebalancing.
        """
        self.funds = initial_funds
        self.return_series = return_series
        self.start_date = start_date
        self.current_date = start_date
        self.end_date = end_date
        self.rebalance_frequency = rebalance_frequency
        self.rebalance_dates = self.generate_rebalance_dates()
        self.allocations = {ticker: 0.0 for ticker in initial_funds}  # Initialize allocations to 0% for each ticker
        self.final_returns = dict()
        self.final_returns[self.start_date] = initial_funds["cash"]
    
    def calculate_returns(self, hist_data, adjclose=True):
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
        full_return_series = pandas.Series([full_return], index=[datetime.datetime.combine(hist_data.index[-1], datetime.time())])

        # Calculate other types of returns
        annually_returns = total_return_data.resample("Y").ffill().pct_change().fillna(0)
        annually_returns.index = [*annually_returns.index[:-1], datetime.datetime.combine(hist_data.index[-1], datetime.time())]
        semi_annually_returns = total_return_data.resample("6M").ffill().pct_change().fillna(0)
        semi_annually_returns.index = [*semi_annually_returns.index[:-1], datetime.datetime.combine(hist_data.index[-1], datetime.time())]
        quarterly_returns = total_return_data.resample("Q").ffill().pct_change().fillna(0)
        quarterly_returns.index = [*quarterly_returns.index[:-1], datetime.datetime.combine(hist_data.index[-1], datetime.time())]
        monthly_returns = total_return_data.resample("M").ffill().pct_change().fillna(0)
        monthly_returns.index = [*monthly_returns.index[:-1], datetime.datetime.combine(hist_data.index[-1], datetime.time())]
        weekly_returns = total_return_data.resample("W").ffill().pct_change().fillna(0)
        weekly_returns.index = [*weekly_returns.index[:-1], datetime.datetime.combine(hist_data.index[-1], datetime.time())]
        daily_returns = total_return_data.pct_change().fillna(0)
        
        # Return a dictionary containing all the calculated returns
        return {
            RDO["NEVER"]["returns"]: full_return_series,
            RDO["ANNUALLY"]["returns"]: annually_returns,
            RDO["SEMI_ANNUALLY"]["returns"]: semi_annually_returns,
            RDO["QUARTERLY"]["returns"]: quarterly_returns,
            RDO["MONTHLY"]["returns"]: monthly_returns,
            RDO["WEEKLY"]["returns"]: weekly_returns,
            RDO["DAILY"]["returns"]: daily_returns
        }

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

    def balance(self, initial_cash):
        """
        Initial balance of the portfolio.
        Represents the first day of depositing the money into the market.
        """
        for ticker in self.funds:
            self.funds[ticker] = initial_cash * self.allocations.get(ticker, 0) / 100
        self.final_returns[self.end_date] = self.get_total_value(returns_type=self.rebalance_frequency["returns"], until=self.end_date)

    def rebalance(self):
        """
        Rebalances the portfolio to maintain the allocation ratios.
        This is typically called after the market values have changed.
        """
        for date in self.rebalance_dates:
            balance_per_period = self.get_total_value(returns_type=self.rebalance_frequency["returns"], until=date)
            self.balance(balance_per_period)
            self.final_returns[date] = balance_per_period

    def generate_rebalance_dates(self):
        """
        Generates a list of rebalance dates based on the specified frequency.

        Returns:
            list: A list of rebalance dates.
        """
        if self.rebalance_frequency == RDO["NEVER"]["name"]:
            return [self.end_date]  # Only the end date for "NEVER" frequency

        frequencies = {
            RDO["MONTHLY"]["name"]: relativedelta(months=+1),
            RDO["QUARTERLY"]["name"]: relativedelta(months=+3),
            RDO["SEMI_ANNUALLY"]["name"]: relativedelta(months=+6),
            RDO["ANNUALLY"]["name"]: relativedelta(years=+1)
        }
        delta = frequencies.get(self.rebalance_frequency["name"])
        dates = []
        current_date = self.start_date
        while current_date <= self.end_date:
            if delta:  # Adjust to get the last day of the month for all frequencies except "never"
                current_date = last_day_of_month(current_date)
            if current_date != self.start_date:
                dates.append(current_date)
            if delta is None:  # Should not reach here for "never", but just as a safeguard
                break
            current_date += delta
        if self.end_date not in dates:
            dates.append(self.end_date)
        return dates
    
    def get_total_value(self, returns_type, until):
        """
        Calculates the total value of the portfolio for all tickers.

        Returns:
            float: The total value of the portfolio.
        """
        total_value = 0
        for ticker, returns in self.return_series.items():
            current_growth = returns[returns_type].loc[datetime.datetime.combine(until, datetime.time())] if not returns[returns_type].empty else 0
            total_value += self.funds.get(ticker, 0) * (1 + current_growth)
        return total_value + self.funds["cash"]
    
    def calculate_cagr(self):
        """
        Calculates the Compound Annual Growth Rate (CAGR) of the portfolio.
        """
        years = (self.end_date - self.start_date).days / 365.25
        values = collections.OrderedDict(sorted(self.final_returns.items()))
        start_value = list(values.values())[0]
        end_value = list(values.values())[-1]
        return (end_value / start_value) ** (1 / years) - 1

    def calculate_stdev(self):
        """
        Calculates the standard deviation of the portfolio's total returns over time.
        """
        # Check if final_returns is empty or has only one element
        if not self.final_returns or len(self.final_returns) < 2:
            return 0

        # Sorting the final_returns
        values = collections.OrderedDict(sorted(self.final_returns.items()))

        # Extract return values from final_returns
        returns = list(values.values())

        # Calculate the percentage change in returns, handling division by zero
        pct_change_returns = []
        for i in range(1, len(returns)):
            if returns[i-1] != 0:
                change = ((returns[i] - returns[i-1]) / returns[i-1])
                pct_change_returns.append(change)

        # Return sample standard deviation using numpy
        return numpy.std(pct_change_returns)

    def calculate_max_drawdown(self):
        """
        Calculates the maximum drawdown of the portfolio.
        """
        values = collections.OrderedDict(sorted(self.final_returns.items()))
        peak = list(values.values())[0]  # Starting with the first value as the initial peak
        max_drawdown = 0
        for _, value in values.items():
            if value > peak:
                peak = value  # Update the peak if current value is higher
            drawdown = (peak - value) / peak if peak != 0 else 0  # Calculate drawdown
            max_drawdown = max(max_drawdown, drawdown)  # Update max_drawdown if current drawdown is higher
        return max_drawdown
    
    def calculate_sharpe_ratio(self, risk_free_rate):
        # Ensure there are final returns to calculate the Sharpe Ratio
        if not self.final_returns:
            return None

        # Calculate portfolio returns as percentage change
        values = collections.OrderedDict(sorted(self.final_returns.items()))
        returns = list(values.values())
        pct_change_returns = [(returns[i] - returns[i - 1]) / returns[i - 1] for i in range(1, len(returns))]

        # Convert list of returns into a numpy array for calculation
        returns_array = numpy.array(pct_change_returns)

        # Calculate the average of annual returns
        mean_return = numpy.mean(returns_array)

        # Since these are already annual returns, no further annualization is needed
        annualized_return = mean_return

        # Annualized standard deviation (already correct)
        annualized_std_deviation = numpy.std(returns_array)

        # Calculate the Sharpe Ratio
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_std_deviation if annualized_std_deviation != 0 else float('nan')

        return sharpe_ratio
    
    def __str__(self):
        """
        String representation of the BasePortfolio object.

        Returns:
            str: A string showing the portfolio allocation and final returns.
        """
        allocation_str = ", ".join([f"{ticker}: {alloc}%" for ticker, alloc in self.allocations.items()])
        final_returns_str = "\n".join([f"{date.strftime('%Y-%m-%d')}: {value:.2f}" for date, value in self.final_returns.items()])
        return f"Portfolio Allocation: {allocation_str}\nFinal Returns:\n{final_returns_str}"

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
    full_return_series = pandas.Series([full_return], index=[datetime.datetime.combine(hist_data.index[-1], datetime.time())])

    # Calculate other types of returns
    annually_returns = total_return_data.resample("Y").ffill().pct_change().fillna(0)
    annually_returns.index = [*annually_returns.index[:-1], datetime.datetime.combine(hist_data.index[-1], datetime.time())]
    semi_annually_returns = total_return_data.resample("6M").ffill().pct_change().fillna(0)
    semi_annually_returns.index = [*semi_annually_returns.index[:-1], datetime.datetime.combine(hist_data.index[-1], datetime.time())]
    quarterly_returns = total_return_data.resample("Q").ffill().pct_change().fillna(0)
    quarterly_returns.index = [*quarterly_returns.index[:-1], datetime.datetime.combine(hist_data.index[-1], datetime.time())]
    monthly_returns = total_return_data.resample("M").ffill().pct_change().fillna(0)
    monthly_returns.index = [*monthly_returns.index[:-1], datetime.datetime.combine(hist_data.index[-1], datetime.time())]
    weekly_returns = total_return_data.resample("W").ffill().pct_change().fillna(0)
    weekly_returns.index = [*weekly_returns.index[:-1], datetime.datetime.combine(hist_data.index[-1], datetime.time())]
    daily_returns = total_return_data.pct_change().fillna(0)
    
    # Return a dictionary containing all the calculated returns
    return {
        RDO["NEVER"]["returns"]: full_return_series,
        RDO["ANNUALLY"]["returns"]: annually_returns,
        RDO["SEMI_ANNUALLY"]["returns"]: semi_annually_returns,
        RDO["QUARTERLY"]["returns"]: quarterly_returns,
        RDO["MONTHLY"]["returns"]: monthly_returns,
        RDO["WEEKLY"]["returns"]: weekly_returns,
        RDO["DAILY"]["returns"]: daily_returns
    }

def last_day_of_month(any_day):
    """Return the last day of the month of any_day"""
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)