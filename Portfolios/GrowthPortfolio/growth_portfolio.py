class GrowthPortfolio:
    def __init__(self, initial_funds):
        self.funds = initial_funds
        self.growth_stocks = 0.0  # Percentage of funds in growth stocks
        self.dividend_stocks = 0.0  # Percentage of funds in dividend stocks
        self.cash = 100.0  # Percentage of funds in cash

    def allocate(self, growth_stocks_percent, dividend_stocks_percent):
        """ Allocate funds into growth stocks and dividend stocks based on given percentages. """
        if growth_stocks_percent + dividend_stocks_percent > 100:
            raise ValueError("Total allocation exceeds 100%")

        self.growth_stocks = growth_stocks_percent
        self.dividend_stocks = dividend_stocks_percent
        self.cash = 100 - growth_stocks_percent - dividend_stocks_percent

    def rebalance(self):
        """ Rebalance the portfolio to maintain the allocation percentages. """
        total_value = self.get_total_value()
        self.funds['growth_stocks'] = total_value * self.growth_stocks / 100
        self.funds['dividend_stocks'] = total_value * self.dividend_stocks / 100
        self.funds['cash'] = total_value * self.cash / 100

    def get_total_value(self):
        """ Calculate the total value of the portfolio. """
        return sum(self.funds.values())

    def __str__(self):
        return f"Portfolio Allocation: {self.growth_stocks}% Growth Stocks, {self.dividend_stocks}% Dividend Stocks, {self.cash}% Cash"

# Example Usage:
portfolio = GrowthPortfolio(initial_funds={'growth_stocks': 15000, 'dividend_stocks': 5000, 'cash': 5000})
portfolio.allocate(growth_stocks_percent=60, dividend_stocks_percent=20)
print(portfolio)
