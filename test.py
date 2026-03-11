from data.fetcher import data_fetcher
from core.portfolio import portfolio
from core.analyser import analyser
from core.optimiser import optimiser
import numpy as np

# fetcher
tickers = ['AAPL', 'NVDA', 'TSLA']
weights = [0.4, 0.35, 0.25]

fetcher = data_fetcher(tickers, 5)
prices_df = fetcher.fetch_daily()
spy_df = fetcher.fetch_spy()

# portfolio
p = portfolio(tickers, weights, prices_df)

# analyser
a = analyser(spy_df, p.returns_df, p.covariance_matrix, p.weights, p.portfolio_volatility)

# optimiser
o = optimiser(p.weights, p.expected_returns_df, p.covariance_matrix)

print("=== PORTFOLIO ===")
print("Expected Return:", p.portfolio_expected_return)
print("Volatility:", p.portfolio_volatility)
print("Sharpe Ratio:", p.sharpe_ratio)

print("\n=== ANALYSER ===")
print("Beta per asset:\n", a.beta_per_asset)
print("Risk Contribution:\n", a.RC_percent)
print("Max Drawdown:\n", a.max_drawdown)

print("\n=== OPTIMISER ===")
print("Max Sharpe Portfolio:\n", o.monte_carlo_df.loc[o.max_sharpe])
print("Min Variance Portfolio:\n", o.monte_carlo_df.loc[o.get_min_variance()])