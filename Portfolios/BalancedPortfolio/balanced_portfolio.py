import datetime

class BalancedPortfolio():
    def __init__(self, initial_funds: dict, stock_growth_rate: float, bond_growth_rate: float, start_date: datetime):
        self.funds = initial_funds
        self.stock_growth_rate = stock_growth_rate
        self.bond_growth_rate = bond_growth_rate
        self.start_date = start_date
        self.current_date = start_date
        self.stocks = 0.0
        self.bonds = 0.0
        self.cash = 100.0

    def allocate(self, stocks_percent, bonds_percent):
        if stocks_percent + bonds_percent > 100:
            raise ValueError("Total allocation exceeds 100%")
        self.stocks = stocks_percent
        self.bonds = bonds_percent
        self.cash = 100 - stocks_percent - bonds_percent

    def rebalance(self):
        total_value = self.get_total_value()
        self.funds['stocks'] = total_value * self.stocks / 100
        self.funds['bonds'] = total_value * self.bonds / 100
        self.funds['cash'] = total_value * self.cash / 100

    def update_date(self, new_date):
        self.current_date = new_date

    def get_total_value(self):
        days_passed = (self.current_date - self.start_date).days
        years_passed = days_passed / 365.25
        current_stocks_value = self.funds['stocks'] * (1 + self.stock_growth_rate) ** years_passed
        current_bonds_value = self.funds['bonds'] * (1 + self.bond_growth_rate) ** years_passed
        return current_stocks_value + current_bonds_value + self.funds['cash']

    def __str__(self):
        return f"Portfolio Allocation: {self.stocks}% Stocks, {self.bonds}% Bonds, {self.cash}% Cash, Total Value: {self.get_total_value():.2f}"

# Function to calculate annualized return from historical data
def calculate_annualized_return(hist_data):
    start_price = hist_data['close'].iloc[0]
    end_price = hist_data['close'].iloc[-1]
    return (end_price / start_price) - 1