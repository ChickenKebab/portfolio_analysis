import numpy as np
import pandas as pd


class optimiser:

    def __init__(self, weights, expected_returns_df, covariance_matrix, ):
        self.weights = weights
        self.covariance_matrix = covariance_matrix
        self.n = len(weights)
        self.expected_returns_df = expected_returns_df
        self.rf = 0.05
        self.monte_carlo_df = self.calculate_monte_carlo()
        self.max_sharpe = self.get_max_sharpe()
        
    

    def calculate_monte_carlo(self):

        monte_carlo_list = []

        for i in range(10000):
            random_numbers = np.random.random(self.n)
            weights = random_numbers/np.sum(random_numbers)
            portfolio_expected_return = np.dot(weights, self.expected_returns_df)
            portfolio_variance_temp = np.dot(weights, self.covariance_matrix)
            portfolio_variance_temp2 = np.dot(portfolio_variance_temp, weights)
            portfolio_volatility = np.sqrt(portfolio_variance_temp2)
            sharpe_ratio = (portfolio_expected_return - self.rf)/portfolio_volatility
            temp_dict = {
                'weights': weights,
                'expected_return': portfolio_expected_return,
                'volatility': portfolio_volatility,
                'sharpe_ratio': sharpe_ratio
            }
            monte_carlo_list.append(temp_dict)
        
        df = pd.DataFrame(monte_carlo_list)
        return df
    
    def get_max_sharpe(self):
        max_sharpe = self.monte_carlo_df['sharpe_ratio'].idxmax()
        return max_sharpe
    
    def get_min_variance(self):
        lowest_volatility = self.monte_carlo_df['volatility'].idxmin()
        return lowest_volatility
    
    def optimise_for_risk(self, target_volatility):
        filtered = self.monte_carlo_df[abs(self.monte_carlo_df['volatility']-target_volatility) < 0.01]
        best_row = filtered.loc[filtered['sharpe_ratio'].idxmax()]
        return best_row








