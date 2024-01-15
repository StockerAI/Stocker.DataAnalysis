import datetime
import pandas
import Constants.investment_vehicles as IV
import Constants.stock_markets as SM
from Constants.rebalance_date_options import RDO
from api_calls import get_stocks
from Portfolios.BalancedPortfolio.balanced_portfolio import BalancedPortfolio

def main():
    # Set up initial parameters
    initial_start_date = datetime.date(2014, 12, 31)
    # end_date = datetime.date(2015, 1, 31)
    end_date = datetime.date(2021, 5, 28)
    rebalance_frequency = RDO["MONTHLY"]  # Set your desired rebalance frequency

    # Initial cash amount
    cash_initial = 10000

    # Define tickers and their information
    tickers_info = {
        "VOO": {"stock_market": SM.OTHER, "investment_vehicle": IV.ETF},
        "IJH": {"stock_market": SM.OTHER, "investment_vehicle": IV.ETF},
        "VXUS": {"stock_market": SM.NASDAQ, "investment_vehicle": IV.ETF},
        "BND": {"stock_market": SM.NASDAQ, "investment_vehicle": IV.ETF},
        "BNDX": {"stock_market": SM.NASDAQ, "investment_vehicle": IV.ETF},
        "VNQ": {"stock_market": SM.OTHER, "investment_vehicle": IV.ETF},
        "GLD": {"stock_market": SM.OTHER, "investment_vehicle": IV.ETF},
        # Other tickers can be added here
    }

    # tickers_info = {
    #     "VOO": {"stock_market": SM.OTHER, "investment_vehicle": IV.ETF},
    # }

    # Initialize funds for each ticker and add cash
    initial_funds = {ticker: 0 for ticker in tickers_info}
    initial_funds["cash"] = cash_initial

    # Initialize the portfolio with initial funds and dates
    portfolio = BalancedPortfolio(
        initial_funds=initial_funds,
        return_series=dict(),  # Initialize with empty return_series
        start_date=initial_start_date,
        end_date=end_date,
        rebalance_frequency=rebalance_frequency,
        investment_vehicles={ticker: info["investment_vehicle"] for ticker, info in tickers_info.items()}
    )

    # Collect and process stock data
    for ticker, info in tickers_info.items():
        ticker_data = pandas.DataFrame(get_stocks(ticker_names=ticker, stock_market_names=info["stock_market"], starting_date=initial_start_date.strftime("%Y-%m-%d"), ending_date=end_date.strftime("%Y-%m-%d")))
        ticker_data["date"] = pandas.to_datetime(ticker_data["date"]).dt.date
        ticker_data = ticker_data.set_index("date")

        if not ticker_data.empty:
            # Call calculate_returns as a method of the portfolio instance
            full_return = portfolio.calculate_returns(ticker_data, adjclose=True)
            portfolio.return_series[ticker] = full_return
        else:
            print(f"No data for {ticker}")

    portfolio.allocate({"VOO": 35, "IJH": 10, "VXUS": 15, "BND": 30, "BNDX": 5, "VNQ": 3, "GLD": 2})  # Adjust as needed
    # portfolio.allocate({"VOO": 100})  # Adjust as needed
    portfolio.balance(cash_initial)
    portfolio.rebalance()
    print(portfolio)
    print(f"Calculation of {rebalance_frequency['name']} CAGR: {portfolio.calculate_cagr() * 100:.2f}%")
    print(f"Calculation of {rebalance_frequency['name']} Stdev: {portfolio.calculate_stdev() * 100:.2f}%")
    print(f"Calculation of {rebalance_frequency['name']} Max. Drawdown: {portfolio.calculate_max_drawdown() * 100:.2f}%")
    print(f"Calcumation of {rebalance_frequency['name']} Sharpe Ratio: {portfolio.calculate_sharpe_ratio(0.0465):.2f}")

if __name__ == "__main__":
    main()
