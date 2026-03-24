'''
analyser.py

Provides the tools to analyse portfolio risk under Modern Portfolio Theorem.
Specifically:
Measures the maximum drawdown compared to SPY, CAPM Beta, and risk contribution per asset.
'''

import numpy as np
import pandas as pd


class analyser:

    def __init__(self, spy_df, returns_df, covariance_matrix, weights, portfolio_volatility):
        self.spy_df = spy_df
        self.SPY_returns = self.calculate_spy_returns()
        self.returns_df = returns_df
        self.covariance_matrix = covariance_matrix
        self.weights = weights
        self.portfolio_volatility = portfolio_volatility
        self.beta_per_asset = self.calculate_beta_per_asset()
        self.RC_percent = self.calculate_risk_contribution_asset()
        self.max_drawdown = self.calculate_max_drawdown()
    

    def calculate_spy_returns(self):
        spy_returns = self.spy_df.pct_change()
        spy_returns = spy_returns.dropna()
        return spy_returns


    
    def calculate_beta_per_asset(self):
        spy_returns = self.spy_df.pct_change().dropna()
        cov_with_spy = self.returns_df.apply(lambda col: col.cov(spy_returns.iloc[:, 0]))
        var_spy = spy_returns.var().iloc[0]
        beta_per_asset = cov_with_spy / var_spy
        return beta_per_asset

    def calculate_risk_contribution_asset(self):
        MRC = np.dot(self.covariance_matrix, self.weights)/self.portfolio_volatility
        RC = self.weights * MRC
        RC_percent = RC/sum(RC)
        return RC_percent
    
    def calculate_max_drawdown(self):
        cumulative_returns = (1+self.returns_df).cumprod()
        rolling_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - rolling_max)/rolling_max
        max_drawdown = drawdown.min()
        return max_drawdown

