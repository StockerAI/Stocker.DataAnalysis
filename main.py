import pandas
from api_calls import get_tickers, get_stocks, get_company_details

def main():
    # tickers = pandas.DataFrame(get_tickers(ticker_names=['QQQ', 'SPY']))
    # print(tickers)
    stocks = pandas.DataFrame(get_stocks(ticker_names=['QQQ', 'SPY'], starting_date='2021-01-01', ending_date='2021-12-31'))
    print(stocks)
    # company_details = pandas.DataFrame(get_company_details(ticker_names=['QQQ', 'SPY']))
    # print(company_details)

if __name__ == "__main__":
    main()
