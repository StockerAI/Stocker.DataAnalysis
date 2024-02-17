import pandas
import numpy
import datetime
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
        self.daily_returns = pandas.DataFrame(columns=['Returns', 'Change'])
        self.monthly_returns = pandas.DataFrame(columns=['Returns', 'Change'])
        self.annually_returns = pandas.DataFrame(columns=['Returns', 'Change'])
    
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
    
    def calculate_monthly_returns(self):
        """
        Calculate the returns on the actual last trading day of each month.
        """
        # Ensure daily_returns index is a DatetimeIndex
        self.daily_returns.index = pandas.to_datetime(self.daily_returns.index)

        # Iterate over each month within the range of dates in daily_returns
        start_date = self.daily_returns.index.min()
        end_date = self.daily_returns.index.max()
        current_date = start_date

        while current_date <= end_date:
            # Get the last calendar day of the current month
            last_calendar_day = last_day_of_month(current_date)
            
            # Find the closest earlier trading day in daily_returns
            last_trading_day = find_closest_earlier_date(last_calendar_day, self.daily_returns.index)

            if last_trading_day or start_date:
                # Check if the last trading day is already in monthly_returns
                if last_trading_day and last_trading_day not in self.monthly_returns.index:
                    # Get the returns for the last trading day from daily_returns
                    returns = self.daily_returns.loc[last_trading_day, 'Returns']

                    # Create a new DataFrame for this row and use concat to add it
                    new_row = pandas.DataFrame({'Returns': [returns]}, index=[last_trading_day])
                    self.monthly_returns = pandas.concat([self.monthly_returns, new_row])
                
                if start_date and start_date not in self.monthly_returns.index:
                    # Get the returns for the last trading day from daily_returns
                    returns = self.daily_returns.loc[start_date, 'Returns']

                    # Create a new DataFrame for this row and use concat to add it
                    new_row = pandas.DataFrame({'Returns': [returns]}, index=[start_date])
                    self.monthly_returns = pandas.concat([self.monthly_returns, new_row])

            # Move to the next month
            current_date = last_calendar_day + datetime.timedelta(days=1)

        # Calculate monthly 'Change' column based on 'Returns'
        self.monthly_returns['Change'] = self.monthly_returns['Returns'].pct_change()

        # Ensure the DataFrame is properly sorted by date
        self.monthly_returns.sort_index(inplace=True)
    
    def calculate_annually_returns(self):
        """
        Calculate the returns on the actual last trading day of each year, 
        including the first and last days' values if the date span is less than a year.
        """
        # Ensure daily_returns index is a DatetimeIndex
        self.daily_returns.index = pandas.to_datetime(self.daily_returns.index)

        # Create an empty DataFrame for annually_returns if it doesn't exist
        if not hasattr(self, 'annually_returns'):
            self.annually_returns = pandas.DataFrame(columns=['Returns'])

        start_date = self.daily_returns.index.min()
        end_date = self.daily_returns.index.max()

        # Check if the span is less than a year
        if (end_date - start_date).days < 365:
            # Add the first day's return
            if start_date not in self.annually_returns.index:
                start_returns = self.daily_returns.loc[start_date, 'Returns']
                new_row_start = pandas.DataFrame({'Returns': [start_returns]}, index=[start_date])
                self.annually_returns = pandas.concat([self.annually_returns, new_row_start])

            # Add the last day's return
            if end_date not in self.annually_returns.index:
                end_returns = self.daily_returns.loc[end_date, 'Returns']
                new_row_end = pandas.DataFrame({'Returns': [end_returns]}, index=[end_date])
                self.annually_returns = pandas.concat([self.annually_returns, new_row_end])

        else:
            # Iterate over each year within the range of dates in daily_returns
            start_year = start_date.year
            end_year = end_date.year

            for year in range(start_year, end_year + 1):
                # Get the last calendar day of December for the current year
                last_calendar_day_of_year = pandas.Timestamp(year=year, month=12, day=31)

                # Find the closest earlier trading day in daily_returns
                last_trading_day_of_year = find_closest_earlier_date(last_calendar_day_of_year, self.daily_returns.index)

                if last_trading_day_of_year:
                    # Check if the last trading day is already in annually_returns
                    if last_trading_day_of_year not in self.annually_returns.index:
                        # Get the returns for the last trading day from daily_returns
                        returns = self.daily_returns.loc[last_trading_day_of_year, 'Returns']

                        # Create a new DataFrame for this row and use concat to add it
                        new_row = pandas.DataFrame({'Returns': [returns]}, index=[last_trading_day_of_year])
                        self.annually_returns = pandas.concat([self.annually_returns, new_row])

        # Calculate annual 'Change' column based on 'Returns', if desired
        self.annually_returns['Change'] = self.annually_returns['Returns'].pct_change()

        # Ensure the DataFrame is properly sorted by date
        self.annually_returns.sort_index(inplace=True)

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
        self.calculate_daily_returns(self.start_date)

    def calculate_daily_returns(self, current_date):
        """
        Update daily returns from a given start date to the end date.
        """
        self.generate_rebalance_dates()

        for current_date in self.useful_dates:
            daily_portfolio_value = self.get_total_value(returns_type="daily_returns", until=current_date)
            
            # Create a new DataFrame for the current day's return
            new_row = pandas.DataFrame({'Returns': [daily_portfolio_value]}, index=[pandas.to_datetime(current_date)])
            
            # Use pandas.concat to add the new row to self.daily_returns
            self.daily_returns = pandas.concat([self.daily_returns, new_row])
            
            if current_date in self.rebalance_dates:
                # At this point, self.daily_returns contains all the rows up to the current date
                self.rebalance()
        
        # Calculate daily percentage change
        self.daily_returns['Change'] = self.daily_returns['Returns'].pct_change()

    def rebalance(self):
        """
        Rebalances the portfolio to maintain the allocation ratios.
        This is typically called after the market values have changed.
        """
        # Assuming 'Returns' is the column name in the DataFrame you want to use
        for ticker in self.funds:
            # Get the last value from the 'Returns' column for the given ticker
            last_return = self.daily_returns['Returns'].iloc[-1]
            
            # Update the fund value for the ticker based on the last return and the allocation ratio
            self.funds[ticker] = last_return * self.allocations.get(ticker, 0) / 100

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
        if self.daily_returns.empty:
            return 0  # Handle case with no returns data
        
        # Ensure the index is in datetime format and sort the DataFrame to ensure chronological order
        self.daily_returns.index = pandas.to_datetime(self.daily_returns.index)
        self.daily_returns.sort_index(inplace=True)
        
        # Get start and end dates from the DataFrame's index
        start_date = self.daily_returns.index[0]
        end_date = self.daily_returns.index[-1]
        
        # Get start and end values from the 'Returns' column
        start_value = self.daily_returns['Returns'].iloc[0]
        end_value = self.daily_returns['Returns'].iloc[-1]
        
        # Calculate the number of years between start and end dates
        years = (end_date - start_date).days / 365.25
        
        # Calculate CAGR
        cagr = (end_value / start_value) ** (1 / years) - 1
        return cagr

    def calculate_stdev(self):
        if len(self.monthly_returns) < 2:
            return {'monthly': 0}  # Not enough data to calculate standard deviation

        # Calculate standard deviation for monthly 'Change' from self.monthly_returns
        self.monthly_returns['Change'].dropna(inplace=True)
        monthly_stdev = self.monthly_returns['Change'].std()
        self.annually_returns['Change'].dropna(inplace=True)
        annually_stdev = self.annually_returns['Change'].std()

        return {'monthly': monthly_stdev, 'annually': annually_stdev}

    def calculate_max_drawdown(self):
        if self.monthly_returns.empty:
            return 0  # Handle case with no returns data
        
        self.monthly_returns['Change'].fillna(0, inplace=True)

        # Calculate cumulative returns from monthly 'Change'
        cumulative_returns = (1 + self.monthly_returns['Change']).cumprod()

        # Initialize variables to track peak, trough, and max drawdown
        peak = cumulative_returns.iloc[0]
        max_drawdown = 0

        # Iterate over the cumulative returns to calculate drawdowns
        for cum_return in cumulative_returns:
            # If new peak is found, update peak
            if cum_return > peak:
                peak = cum_return

            # Calculate drawdown from peak to current point
            drawdown = (peak - cum_return) / peak

            # Update max drawdown if this drawdown is larger than the previous max drawdown
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        return max_drawdown

    # def calculate_sharpe_ratio(self, mean_monthly_excess_return, periods_per_year=12):
    #     """
    #     Calculate the annualized Sharpe Ratio.

    #     Parameters:
    #     mean_monthly_excess_return (float): The mean monthly excess return of the portfolio over the risk-free rate.
    #     periods_per_year (int, optional): The number of periods in a year, default is 12 for monthly data.

    #     Returns:
    #     float: The annualized Sharpe Ratio.
    #     """
    #     stdev_dict = self.calculate_stdev()  # This returns a dictionary
    #     monthly_stdev = stdev_dict['monthly']  # Extract the monthly standard deviation
    #     if monthly_stdev == 0:  # Prevent division by zero
    #         return 0
    #     sharpe_ratio = mean_monthly_excess_return / monthly_stdev
    #     annualized_sharpe_ratio = sharpe_ratio * numpy.sqrt(periods_per_year)
    #     return annualized_sharpe_ratio

    def __str__(self):
        """
        String representation of the BasePortfolio object.

        Returns:
            str: A string showing the portfolio allocation and the returns on the actual last trading day of each month.
        """
        allocation_str = ", ".join([f"{ticker}: {alloc}%" for ticker, alloc in self.allocations.items()])

        self.calculate_monthly_returns()
        self.calculate_annually_returns()

        with pandas.option_context('display.max_rows', None,
                       'display.max_columns', None,
                    #    'display.precision', 3,
                       ):
            print(self.annually_returns)

        # Format the monthly returns for the string representation
        monthly_returns_str = "\n".join([f"{date.strftime('%Y-%m-%d')}: Returns: {row['Returns']:.2f}, Change: {row['Change'] * 100:.2f}%" for date, row in self.monthly_returns.iterrows()])

        return f"Portfolio Allocation: {allocation_str}\nReturns on Actual Last Trading Day of Each Month:\n{monthly_returns_str}"

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
    earlier_dates = [date for date in date_list if date <= target_date]
    if not earlier_dates:
        return None
    return min(earlier_dates, key=lambda date: (target_date - date).days)
