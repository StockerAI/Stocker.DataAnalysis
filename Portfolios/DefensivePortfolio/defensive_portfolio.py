class DefensivePortfolio:
    def __init__(self, initial_funds):
        self.funds = initial_funds
        self.bonds = 0.0  # Percentage of funds in bonds
        self.defensive_stocks = 0.0  # Percentage of funds in defensive stocks
        self.cash = 100.0  # Percentage of funds in cash

    def allocate(self, bonds_percent, defensive_stocks_percent):
        """ Allocate funds into bonds and defensive stocks based on given percentages. """
        if bonds_percent + defensive_stocks_percent > 100:
            raise ValueError("Total allocation exceeds 100%")

        self.bonds = bonds_percent
        self.defensive_stocks = defensive_stocks_percent
        self.cash = 100 - bonds_percent - defensive_stocks_percent

    def rebalance(self):
        """ Rebalance the portfolio to maintain the allocation percentages. """
        total_value = self.get_total_value()
        self.funds['bonds'] = total_value * self.bonds / 100
        self.funds['defensive_stocks'] = total_value * self.defensive_stocks / 100
        self.funds['cash'] = total_value * self.cash / 100

    def get_total_value(self):
        """ Calculate the total value of the portfolio. """
        return sum(self.funds.values())

    def __str__(self):
        return f"Portfolio Allocation: {self.bonds}% Bonds, {self.defensive_stocks}% Defensive Stocks, {self.cash}% Cash"

# Example Usage:
portfolio = DefensivePortfolio(initial_funds={'bonds': 10000, 'defensive_stocks': 8000, 'cash': 12000})
portfolio.allocate(bonds_percent=40, defensive_stocks_percent=35)
print(portfolio)
