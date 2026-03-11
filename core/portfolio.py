import numpy as np
import pandas as pd

class portfolio:

    def __init__(self, tickers, weights, prices_df):
        self.tickers = tickers
        self.weights = np.array(weights)
        self.prices_df = prices_df
        self.rf = 0.005
        self.returns_df = self.calculate_daily_return()
        self.expected_returns_df = self.calculate_expected_returns()
        self.covariance_matrix = self.calculate_covariance_matrix()
        self.correlation_matrix = self.calculate_correlation_matrix()
        self.portfolio_expected_return = self.calculate_portfolio_expected_return()
        self.portfolio_variance = self.calculate_portfolio_variance()
        self.portfolio_volatility = self.calculate_portfolio_volatility()
        self.sharpe_ratio = self.calculate_sharpe_ratio()

    def calculate_daily_return(self):
        returns_df = self.prices_df.pct_change()
        returns_df = returns_df.dropna()
        return returns_df
    
    def calculate_expected_returns(self):
        expected_returns_df = self.returns_df.mean() * 252
        return expected_returns_df
    
    def calculate_covariance_matrix(self):
        covariance_matrix = self.returns_df.cov() * 252
        return covariance_matrix

    def calculate_correlation_matrix(self):
        correlation_matrix = self.returns_df.corr()
        return correlation_matrix
    
    def calculate_portfolio_expected_return(self):
        portfolio_expected_return = np.dot(self.weights, self.expected_returns_df)
        return portfolio_expected_return

    def calculate_portfolio_variance(self):
        portfolio_variance_temp = np.dot(self.weights, self.covariance_matrix)
        portfolio_variance = np.dot(portfolio_variance_temp, self.weights)
        return portfolio_variance
    
    def calculate_portfolio_volatility(self):
        portfolio_volatility = np.sqrt(self.portfolio_variance)
        return portfolio_volatility
    
    def calculate_sharpe_ratio(self):
        sharpe_ratio = (self.portfolio_expected_return - self.rf)/self.portfolio_volatility
        return sharpe_ratio


    

    
    
        