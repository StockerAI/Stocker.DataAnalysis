import pandas
import datetime
from dateutil.relativedelta import relativedelta
import Constants.investment_vehicles as IV
import Constants.stock_markets as SM
import Constants.rebalance_date_options as RDO
from api_calls import get_stocks
from Portfolios.BalancedPortfolio.balanced_portfolio import BalancedPortfolio
from Portfolios.base_portfolio import calculate_returns

def last_day_of_month(any_day):
    """Return the last day of the month of any_day"""
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)

def generate_rebalance_dates(start_date, end_date, frequency=RDO.NEVER):
    if frequency == RDO.NEVER:
        return [end_date]  # Only the end date for 'NEVER' frequency

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
        if delta:  # Adjust to get the last day of the month for all frequencies except 'never'
            current_date = last_day_of_month(current_date)
        dates.append(current_date)
        if delta is None:  # Should not reach here for 'never', but just as a safeguard
            break
        current_date += delta
    # if end_date not in dates:
    #     dates.append(end_date)
    return dates

def main():
    initial_start_date = datetime.date(2018, 12, 31)
    end_date = datetime.date(2019, 12, 31)
    rebalance_frequency = RDO.MONTHLY

    rebalance_dates = generate_rebalance_dates(initial_start_date, end_date, rebalance_frequency)

    # Initialize cash for the very first period
    cash_initial = 10000

    for i, current_rebalance_date in enumerate(rebalance_dates):
        starting_date = initial_start_date if i == 0 else rebalance_dates[i - 1]
        ending_date = current_rebalance_date

        str_starting_date = starting_date.strftime("%Y-%m-%d")
        str_ending_date = ending_date.strftime("%Y-%m-%d")
        
        tickers_info = {
            "MSFT": {"stock_market": SM.SP500, "asset_type": IV.STOCK},
            "AAPL": {"stock_market": SM.SP500, "asset_type": IV.STOCK}
            # Other tickers can be added here
        }

        # Initialize funds for each ticker and add cash
        initial_funds = {ticker: 0 for ticker in tickers_info}
        initial_funds["cash"] = cash_initial

        return_series = {}

        for ticker, info in tickers_info.items():
            ticker_data = pandas.DataFrame(get_stocks(ticker_names=ticker, stock_market_names=info["stock_market"], starting_date=str_starting_date, ending_date=str_ending_date))
            ticker_data["date"] = pandas.to_datetime(ticker_data["date"]).dt.date
            ticker_data = ticker_data.set_index("date")

            if not ticker_data.empty:
                full_return = calculate_returns(ticker_data, adjclose=False)["full_return"]
                return_series[ticker] = full_return
            else:
                print(f"No data for {ticker}")

        portfolio = BalancedPortfolio(initial_funds=initial_funds, return_series=return_series, start_date=starting_date, asset_types={ticker: info["asset_type"] for ticker, info in tickers_info.items()})
        portfolio.allocate({"MSFT": 60, "AAPL": 40})  # Adjust as needed
        portfolio.update_date(ending_date)
        portfolio.rebalance()

        # Update cash_initial for the next period
        cash_initial = portfolio.get_total_value()
        if rebalance_frequency != RDO.NEVER:
            print(f"Rebalancing on: {current_rebalance_date.strftime('%Y-%m-%d')}, Portfolio Value: {cash_initial}")
    print(f"Final balance on: {end_date.strftime('%Y-%m-%d')}, Portfolio Value: {portfolio.get_total_value()}")

if __name__ == "__main__":
    main()
