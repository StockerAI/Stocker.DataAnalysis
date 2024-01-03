import pandas
import datetime
from api_calls import get_tickers, get_stocks, get_company_details
from Portfolios.BalancedPortfolio.balanced_portfolio import BalancedPortfolio, calculate_annualized_return

def main():
    starting_date = '2022-12-31'
    ending_date = '2023-12-31'
    # Fetch historical data using Stocker.API
    aapl_data = pandas.DataFrame(get_stocks(ticker_names="AAPL", starting_date=starting_date, ending_date=ending_date))
    agg_data = pandas.DataFrame(get_stocks(ticker_names="AGG", starting_date=starting_date, ending_date=ending_date))

    # Calculate annualized returns
    aapl_return = calculate_annualized_return(aapl_data)
    agg_return = calculate_annualized_return(agg_data)

    # Initialize and operate the portfolio
    initial_funds = {'stocks': 0, 'bonds': 0, 'cash': 10000}
    portfolio = BalancedPortfolio(initial_funds=initial_funds, stock_growth_rate=aapl_return, bond_growth_rate=agg_return, start_date=datetime.datetime(2023, 1, 1))
    portfolio.allocate(100, 0)
    portfolio.update_date(datetime.datetime(2024, 1, 1))
    portfolio.rebalance()

    # Print the portfolio status
    print(portfolio)

if __name__ == "__main__":
    main()
