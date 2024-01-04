import pandas
import datetime
from api_calls import get_tickers, get_stocks, get_company_details
from Portfolios.BalancedPortfolio.balanced_portfolio import BalancedPortfolio, calculate_returns

import pandas
import datetime

def main():
    starting_date = "2021-12-31"
    ending_date = "2022-12-31"
    tickers = ["MSFT", "PG", "JNJ", "CVX", "FLGV", "AAPL"]  # Example tickers
    stock_market_names = {"MSFT": "NASDAQ", "PG": "OTHER", "JNJ": "DOW", "CVX": "DOW", "FLGV": "OTHER", "AAPL": "NASDAQ"}  # Stock markets for each ticker

    # Initialize dictionaries for funds and return series
    initial_funds = {ticker: 0 for ticker in tickers}
    initial_funds["cash"] = 10000  # Adding cash to the portfolio
    return_series = {}

    for ticker in tickers:
        # Fetch historical data for each ticker from its respective stock market
        ticker_data = pandas.DataFrame(get_stocks(ticker_names=ticker, stock_market_names=stock_market_names[ticker], starting_date=starting_date, ending_date=ending_date))
        ticker_data["date"] = pandas.to_datetime(ticker_data["date"])
        ticker_data = ticker_data.set_index("date")

        # Calculate annualized returns for each ticker
        full_return = calculate_returns(ticker_data, adjclose=True)["full_return"]
        return_series[ticker] = full_return

    # Initialize and operate the portfolio
    portfolio = BalancedPortfolio(initial_funds=initial_funds, return_series=return_series, start_date=datetime.datetime(2021, 12, 31))
    portfolio.allocate({"MSFT": 15, "PG": 15, "JNJ": 15, "CVX": 15, "FLGV": 20, "AAPL": 20})  # Allocating percentages to each ticker
    portfolio.update_date(datetime.datetime(2022, 12, 31))
    portfolio.rebalance()

    # Print the portfolio status
    print(portfolio)

if __name__ == "__main__":
    main()
