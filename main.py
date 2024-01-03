import pandas
import datetime
from api_calls import get_tickers, get_stocks, get_company_details
from Portfolios.BalancedPortfolio.balanced_portfolio import BalancedPortfolio, calculate_returns

def main():
    starting_date = '2021-12-31'
    ending_date = '2022-12-31'
    # Fetch historical data using Stocker.API
    aapl_data = pandas.DataFrame(get_stocks(ticker_names="AAPL", stock_market_names="NASDAQ", starting_date=starting_date, ending_date=ending_date))
    agg_data = pandas.DataFrame(get_stocks(ticker_names="AGG", stock_market_names="OTHER", starting_date=starting_date, ending_date=ending_date))

    # Convert the date column to datetime and set it as the index
    aapl_data['date'] = pandas.to_datetime(aapl_data['date'])
    aapl_data = aapl_data.set_index('date')

    # Convert the date column to datetime and set it as the index
    agg_data['date'] = pandas.to_datetime(agg_data['date'])
    agg_data = agg_data.set_index('date')

    # Calculate annualized returns
    aapl_return = calculate_returns(aapl_data)['full_return']
    aapl_returns = calculate_returns(aapl_data)
    # print(aapl_returns['full_return'])

    agg_return = calculate_returns(agg_data)['full_return']
    agg_returns = calculate_returns(agg_data)
    # print(agg_returns['full_return'])

    # Initialize and operate the portfolio
    initial_funds = {'stocks': 0, 'bonds': 0, 'cash': 10000}
    portfolio = BalancedPortfolio(initial_funds=initial_funds, stock_returns=aapl_return, bond_returns=agg_return, start_date=datetime.datetime(2021, 12, 31))
    portfolio.allocate(stocks_percent=50, bonds_percent=50)
    portfolio.update_date(datetime.datetime(2022, 12, 31))
    portfolio.rebalance()

    # Print the portfolio status
    print(portfolio)

if __name__ == "__main__":
    main()
