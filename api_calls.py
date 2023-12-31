import requests

local_path = 'http://127.0.0.1:5000'

def get_tickers(ticker_names):
    url = local_path + '/get_tickers'
    params = {'ticker_name': ticker_names}
    response = requests.get(url, params=params)
    return response.json()

def get_stocks(ticker_names, starting_date,  ending_date):
    url = local_path + '/get_stocks'
    params = {}
    if ticker_names:
        params['ticker_name'] = ticker_names
    if starting_date:
        params['starting_date'] = starting_date
    if ending_date:
        params['ending_date'] = ending_date
    response = requests.get(url, params=params)
    return response.json()

def get_company_details(ticker_names):
    url = local_path + '/get_company_details'
    params = {'ticker_name': ticker_names}
    response = requests.get(url, params=params)
    return response.json()