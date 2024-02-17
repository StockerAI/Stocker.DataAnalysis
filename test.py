import yfinance as yf
from yahoo_fin import stock_info
import yahooquery

spy1 = yf.Ticker('AAPL')

spy2 = yf.Ticker("VFINX")

spy3 = yf.Ticker("SPY").history_metadata

spy4 = yf.Ticker("CGRN")

a = stock_info.get_data("CGRN")

print(a)