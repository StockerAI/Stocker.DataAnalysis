import yfinance as yf
from yahoo_fin import stock_info

class AssetAllocation:
    def __init__(self, stock_allocation):
        self.stock_allocation = stock_allocation

    def set_allocation(self, allocation):
        self.stock_allocation = allocation

    def get_allocation(self):
        return self.stock_allocation

    def __str__(self):
        return f"Stock Allocation: {self.stock_allocation}%"

# Example usage:
# Create an instance of AssetAllocation for a specific stock, e.g., Apple (AAPL)
apple_allocation = AssetAllocation(50)  # 50% allocation in Apple stock

# Fetch the current price of Apple stock using yfinance
apple_stock_price = yf.Ticker("AAPL").info['regularMarketPrice']
print(f"Current price of Apple (AAPL) stock: ${apple_stock_price}")

# Fetch and display P/E ratio using yahoo_fin
apple_pe_ratio = stock_info.get_quote_table("AAPL")['PE Ratio (TTM)']
print(f"Apple (AAPL) P/E Ratio: {apple_pe_ratio}")

# Adjust the allocation if needed
apple_allocation.set_allocation(60)
print(apple_allocation)
