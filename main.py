import pandas
import datetime
import Constants.investment_vehicles as IV
import Constants.stock_markets as SM
from api_calls import get_tickers, get_stocks, get_company_details
from Portfolios.BalancedPortfolio.balanced_portfolio import BalancedPortfolio
from Portfolios.DefensivePortfolio.defensive_portfolio import DefensivePortfolio
from Portfolios.base_portfolio import calculate_returns

def main():
    #-------------------------------------------------------------------------------------#
    #--------------------------------- WITH REBALANCE ------------------------------------#
    #-------------------------------------------------------------------------------------#

    starting_date = "2021-12-31"
    ending_date = "2022-01-31"
    
    # Combined dictionary for tickers
    tickers_info = {
        "MSFT": {"stock_market": SM.NASDAQ, "asset_type": IV.STOCK},
        # "PG":   {"stock_market": SM.OTHER, "asset_type": IV.STOCK},
        # "JNJ":  {"stock_market": SM.DOW, "asset_type": IV.STOCK},
        # "CVX":  {"stock_market": SM.DOW, "asset_type": IV.STOCK},
        # "FLGV": {"stock_market": SM.OTHER, "asset_type": IV.BOND},
        "AAPL": {"stock_market": SM.NASDAQ, "asset_type": IV.STOCK}
    }

    # Initialize dictionaries for funds and return series
    initial_funds = {ticker: 0 for ticker in tickers_info}
    initial_funds["cash"] = 10000  # Adding cash to the portfolio
    return_series = {}

    for ticker, info in tickers_info.items():
        # Fetch historical data for each ticker from its respective stock market
        ticker_data = pandas.DataFrame(get_stocks(ticker_names=ticker, stock_market_names=info["stock_market"], starting_date=starting_date, ending_date=ending_date))
        ticker_data["date"] = pandas.to_datetime(ticker_data["date"])
        ticker_data = ticker_data.set_index("date")

        # Calculate annualized returns for each ticker
        full_return = calculate_returns(ticker_data, adjclose=False)["full_return"]
        return_series[ticker] = full_return

    # Extract asset types from tickers_info
    asset_types = {ticker: info["asset_type"] for ticker, info in tickers_info.items()}

    # Initialize and operate the BalancedPortfolio
    portfolio = BalancedPortfolio(initial_funds=initial_funds, return_series=return_series, start_date=datetime.datetime(2021, 12, 31), asset_types=asset_types)
    # portfolio.allocate({"MSFT": 15, "PG": 15, "JNJ": 15, "CVX": 15, "FLGV": 20, "AAPL": 20})  # Allocating percentages to each ticker
    portfolio.update_date(datetime.datetime(2022, 1, 31))
    portfolio.rebalance()

    # Print the portfolio status
    print(portfolio.get_total_value())



    starting_date = "2022-01-31"
    ending_date = "2022-02-28"
    
    # Combined dictionary for tickers
    tickers_info = {
        "MSFT": {"stock_market": SM.NASDAQ, "asset_type": IV.STOCK},
        # "PG":   {"stock_market": SM.OTHER, "asset_type": IV.STOCK},
        # "JNJ":  {"stock_market": SM.DOW, "asset_type": IV.STOCK},
        # "CVX":  {"stock_market": SM.DOW, "asset_type": IV.STOCK},
        # "FLGV": {"stock_market": SM.OTHER, "asset_type": IV.BOND},
        "AAPL": {"stock_market": SM.NASDAQ, "asset_type": IV.STOCK}
    }

    # Initialize dictionaries for funds and return series
    initial_funds = {ticker: 0 for ticker in tickers_info}
    initial_funds["cash"] = portfolio.get_total_value()  # Adding cash to the portfolio
    return_series = {}

    for ticker, info in tickers_info.items():
        # Fetch historical data for each ticker from its respective stock market
        ticker_data = pandas.DataFrame(get_stocks(ticker_names=ticker, stock_market_names=info["stock_market"], starting_date=starting_date, ending_date=ending_date))
        ticker_data["date"] = pandas.to_datetime(ticker_data["date"])
        ticker_data = ticker_data.set_index("date")

        # Calculate annualized returns for each ticker
        full_return = calculate_returns(ticker_data, adjclose=False)["full_return"]
        return_series[ticker] = full_return

    # Extract asset types from tickers_info
    asset_types = {ticker: info["asset_type"] for ticker, info in tickers_info.items()}

    # Initialize and operate the BalancedPortfolio
    portfolio = BalancedPortfolio(initial_funds=initial_funds, return_series=return_series, start_date=datetime.datetime(2021, 1, 31), asset_types=asset_types)
    # portfolio.allocate({"MSFT": 15, "PG": 15, "JNJ": 15, "CVX": 15, "FLGV": 20, "AAPL": 20})  # Allocating percentages to each ticker
    portfolio.update_date(datetime.datetime(2022, 2, 28))
    portfolio.rebalance()

    # Print the portfolio status
    print(portfolio.get_total_value())


    #-------------------------------------------------------------------------------------#
    #------------------------------ WITHOUT REBALANCE ------------------------------------#
    #-------------------------------------------------------------------------------------#


    starting_date = "2021-12-31"
    ending_date = "2022-02-28"
    
    # Combined dictionary for tickers
    tickers_info = {
        "MSFT": {"stock_market": SM.NASDAQ, "asset_type": IV.STOCK},
        # "PG":   {"stock_market": SM.OTHER, "asset_type": IV.STOCK},
        # "JNJ":  {"stock_market": SM.DOW, "asset_type": IV.STOCK},
        # "CVX":  {"stock_market": SM.DOW, "asset_type": IV.STOCK},
        # "FLGV": {"stock_market": SM.OTHER, "asset_type": IV.BOND},
        "AAPL": {"stock_market": SM.NASDAQ, "asset_type": IV.STOCK}
    }

    # Initialize dictionaries for funds and return series
    initial_funds = {ticker: 0 for ticker in tickers_info}
    initial_funds["cash"] = 10000  # Adding cash to the portfolio
    return_series = {}

    for ticker, info in tickers_info.items():
        # Fetch historical data for each ticker from its respective stock market
        ticker_data = pandas.DataFrame(get_stocks(ticker_names=ticker, stock_market_names=info["stock_market"], starting_date=starting_date, ending_date=ending_date))
        ticker_data["date"] = pandas.to_datetime(ticker_data["date"])
        ticker_data = ticker_data.set_index("date")

        # Calculate annualized returns for each ticker
        full_return = calculate_returns(ticker_data, adjclose=False)["full_return"]
        return_series[ticker] = full_return

    # Extract asset types from tickers_info
    asset_types = {ticker: info["asset_type"] for ticker, info in tickers_info.items()}

    # Initialize and operate the BalancedPortfolio
    portfolio = BalancedPortfolio(initial_funds=initial_funds, return_series=return_series, start_date=datetime.datetime(2021, 12, 31), asset_types=asset_types)
    # portfolio.allocate({"MSFT": 15, "PG": 15, "JNJ": 15, "CVX": 15, "FLGV": 20, "AAPL": 20})  # Allocating percentages to each ticker
    portfolio.update_date(datetime.datetime(2022, 2, 28))
    portfolio.rebalance()

    # Print the portfolio status
    print(portfolio.get_total_value())

if __name__ == "__main__":
    main()
