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
        self.rebalance_dates = list()
        self.allocations = {ticker: 0.0 for ticker in initial_funds}  # Initialize allocations to 0% for each ticker
        self.final_returns = dict()
        self.final_returns[self.start_date] = initial_funds["cash"]
        self.useful_dates = list()
        self.daily_returns = dict()
    
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

        self.useful_dates = [timestamp.date() for timestamp in daily_returns.index]
        
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
        self.update_daily_returns(self.start_date)
    
    def update_daily_returns(self, current_date):
        """
        Update daily returns from a given start date to the end date.
        """
        self.generate_rebalance_dates()
        for current_date in self.useful_dates:
            daily_portfolio_value = self.get_total_value(returns_type="daily_returns", until=current_date)
            self.daily_returns[current_date] = daily_portfolio_value
            if current_date in self.rebalance_dates:
                self.rebalance(current_date)

    def rebalance(self, rebalance_date):
        """
        Rebalances the portfolio to maintain the allocation ratios.
        This is typically called after the market values have changed.
        """
        for ticker in self.funds:
            self.funds[ticker] = list(self.daily_returns.values())[-1] * self.allocations.get(ticker, 0) / 100

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
            if current_date not in self.useful_dates:
                current_date = find_closest_earlier_date(current_date, self.useful_dates)
            if current_date != self.start_date:
                dates.append(current_date)
            if delta is None:  # Should not reach here for "never", but just as a safeguard
                break
            current_date += delta
        if self.end_date not in dates:
            dates.append(self.end_date)
        self.rebalance_dates = dates
    
    def get_total_value(self, returns_type="daily_returns", until=None):
        """
        Calculate the total value of the portfolio until a specified date.

        Parameters:
            returns_type (str): The type of returns to use for the calculation (e.g., "daily_returns").
            until (datetime.date): The date until which to calculate the portfolio value.

        Returns:
            float: The total value of the portfolio.
        """
        if until is None:
            until = self.current_date

        total_value = 0
        for ticker, initial_amount in self.funds.items():
            # Check if the ticker is present in the return series
            if ticker in self.return_series:
                # Retrieve the returns for the ticker
                ticker_returns = self.return_series[ticker][returns_type]

                # Convert the index to a list for easier handling
                ticker_returns_index = [timestamp.date() for timestamp in ticker_returns.index]

                # Find the return up to the specified date
                if until in ticker_returns_index:
                    return_up_to_date = ticker_returns.loc[until.strftime("%Y-%m-%d")]
                else:
                    # If the specific date is not in the returns index, use the last available return
                    return_up_to_date = ticker_returns[:until].iloc[-1]
            else:
                # If ticker is not in return_series, use a default return (e.g., 0 for cash)
                return_up_to_date = 0

            # Calculate the value of this ticker in the portfolio
            ticker_value = initial_amount * (1 + return_up_to_date)
            self.funds[ticker] = ticker_value
            total_value += ticker_value


        return total_value
    
    def calculate_cagr(self):
        if not self.daily_returns:
            return 0  # Handle case with no returns data
        
        # Convert keys to list and sort to ensure chronological order
        dates = sorted(self.daily_returns.keys())
        start_date = dates[0]
        end_date = dates[-1]
        
        # Get start and end values
        start_value = self.daily_returns[start_date]
        end_value = self.daily_returns[end_date]
        
        # Calculate the number of years between start and end dates
        years = (end_date - start_date).days / 365.25
        
        # Calculate CAGR
        cagr = (end_value / start_value) ** (1 / years) - 1
        return cagr

    def calculate_stdev(self):
        if len(self.daily_returns) < 2:
            return {'monthly': 0, 'annual': 0}  # Not enough data to calculate standard deviation

        # Convert daily returns to a Pandas Series for easier manipulation
        dates = list(self.daily_returns.keys())
        values = list(self.daily_returns.values())
        daily_returns = pandas.Series([(values[i] - values[i - 1]) / values[i - 1] for i in range(1, len(values))], index=dates[1:])

        # Ensure the index is a DatetimeIndex
        daily_returns.index = pandas.to_datetime(daily_returns.index)

        # Group by month and calculate monthly returns
        monthly_returns = daily_returns.resample('M').apply(lambda x: (1 + x).prod() - 1)

        # Group by year and calculate annual returns
        annual_returns = daily_returns.resample('Y').apply(lambda x: (1 + x).prod() - 1)

        # Calculate standard deviations
        monthly_stdev = monthly_returns.std()
        annual_stdev = annual_returns.std()

        return {'monthly': monthly_stdev, 'annually': annual_stdev}

    def calculate_max_drawdown(self):
        if not self.daily_returns:
            return 0  # Handle case with no returns data

        # Convert daily_returns to a Pandas DataFrame for easier manipulation
        dates = list(self.daily_returns.keys())
        values = list(self.daily_returns.values())
        daily_returns_df = pandas.DataFrame(values, index=pandas.to_datetime(dates), columns=['Portfolio Value'])

        # Calculate daily percentage returns
        daily_returns_df['Daily Returns'] = daily_returns_df['Portfolio Value'].pct_change()

        # Resample to monthly returns and calculate cumulative product to simulate monthly compounded returns
        monthly_cumulative_returns = (1 + daily_returns_df['Daily Returns'].resample('M').sum()).cumprod()

        # Initialize variables to track peak, trough and max drawdown
        peak = monthly_cumulative_returns[0]
        max_drawdown = 0

        # Iterate over the cumulative returns to calculate drawdowns
        for cum_return in monthly_cumulative_returns:
            # If new peak is found, update peak
            if cum_return > peak:
                peak = cum_return
            
            # Calculate drawdown from peak to current point
            drawdown = (peak - cum_return) / peak

            # Update max drawdown if this drawdown is larger than the previous max drawdown
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        return max_drawdown

    def calculate_sharpe_ratio(self, risk_free_rate):
        if len(self.daily_returns) < 2:
            return None  # Not enough data to calculate Sharpe Ratio

        # Convert daily_returns to a Pandas DataFrame for easier manipulation
        dates = list(self.daily_returns.keys())
        values = list(self.daily_returns.values())
        daily_returns_df = pandas.DataFrame(values, index=pandas.to_datetime(dates), columns=['Portfolio Value'])

        # Calculate daily percentage returns
        daily_returns_df['Daily Returns'] = daily_returns_df['Portfolio Value'].pct_change()

        # Resample to monthly returns
        monthly_returns = daily_returns_df['Daily Returns'].resample('M').sum()

        # Calculate monthly excess returns over the risk-free rate
        # Assuming risk-free rate is an annual rate, divide by 12 to get monthly rate
        monthly_excess_returns = monthly_returns - (risk_free_rate / 12)

        # Calculate mean and standard deviation of monthly excess returns
        mean_excess_return = monthly_excess_returns.mean()
        stdev_excess_return = monthly_excess_returns.std()

        # Annualize the mean excess return and stdev of excess return
        # Assuming 12 periods per year for monthly data
        annualized_mean_excess_return = mean_excess_return * 12
        annualized_stdev_excess_return = stdev_excess_return * (12 ** 0.5)

        # Calculate Sharpe Ratio
        sharpe_ratio = annualized_mean_excess_return / annualized_stdev_excess_return if annualized_stdev_excess_return != 0 else float('nan')

        return sharpe_ratio

    def __str__(self):
        """
        String representation of the BasePortfolio object.

        Returns:
            str: A string showing the portfolio allocation and final returns.
        """
        allocation_str = ", ".join([f"{ticker}: {alloc}%" for ticker, alloc in self.allocations.items()])
        daily_returns_str = "\n".join([f"{date.strftime('%Y-%m-%d')}: {value:.2f}" for date, value in self.daily_returns.items()])
        return f"Portfolio Allocation: {allocation_str}\nDaily Returns:\n{daily_returns_str}"

def last_day_of_month(any_day):
    """Return the last day of the month of any_day"""
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)

def find_closest_earlier_date(target_date, date_list):
    """
    Find the closest date earlier than the target_date in date_list.

    Args:
    target_date (datetime.date): The date to compare to.
    date_list (list of datetime.date): The list of dates to search in.

    Returns:
    datetime.date: The closest earlier date found in the list. 
                   If no earlier date exists, returns None.
    """
    earlier_dates = [date for date in date_list if date < target_date]
    if not earlier_dates:
        return None
    return min(earlier_dates, key=lambda date: (target_date - date).days)