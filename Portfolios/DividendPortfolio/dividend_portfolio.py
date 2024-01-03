class DividendPortfolio:
    def __init__(self, initial_funds):
        self.funds = initial_funds
        self.dividend_stocks = 0.0  # Percentage of funds in dividend-paying stocks
        self.cash = 100.0  # Percentage of funds in cash

    def allocate(self, dividend_stocks_percent):
        """ Allocate funds into dividend-paying stocks based on the given percentage. """
        if dividend_stocks_percent > 100:
            raise ValueError("Allocation exceeds 100%")

        self.dividend_stocks = dividend_stocks_percent
        self.cash = 100 - dividend_stocks_percent

    def rebalance(self):
        """ Rebalance the portfolio to maintain the allocation percentages. """
        total_value = self.get_total_value()
        self.funds['dividend_stocks'] = total_value * self.dividend_stocks / 100
        self.funds['cash'] = total_value * self.cash / 100

    def get_total_value(self):
        """ Calculate the total value of the portfolio. """
        return sum(self.funds.values())

    def __str__(self):
        return f"Portfolio Allocation: {self.dividend_stocks}% Dividend Stocks, {self.cash}% Cash"

# Example Usage:
portfolio = DividendPortfolio(initial_funds={'dividend_stocks': 15000, 'cash': 5000})
portfolio.allocate(dividend_stocks_percent=75)
print(portfolio)
