'''
data_fetcher.py

This file fetches historical data for the stocks that the user has selected and SPY for comparisons.
Originally, this file used yahoo finance but due to the nature of API Limits, OpenBB was chosen in the end.
Overall, this file provides the tools to validate that a ticker is valid, fetch SPY data, fetch any stocks in the S&P 500.
Additionally, it allows the user to select the data range of the analysis.
It is acknowledged that limiting the stock picks to the S&P500 is not ideal. However, this project was simply intended to help understand Portfolio Theory.
'''

import pandas as pd
import time
from openbb import obb

df_tickers = pd.read_csv('constituents.csv')        
tickers = df_tickers['Symbol'].tolist()     


class data_fetcher():

    def __init__(self, tickers, initial_date_range):
        self.tickers = tickers      
        self.initial_date_range = initial_date_range    
    
    def validate(self):
        
        for t in self.tickers:
            if t not in tickers:
                return False
        return True
    
    def fetch_spy(self):

        # Fetches the historical data for spy
        spy_df = obb.equity.price.historical('SPY', start_date='2020-01-01', )
        spy_df = spy_df.to_df()
        spy_df = spy_df[['close']].rename(columns={'close': 'SPY'})
        return spy_df
    
    def fetch_daily(self):

        # Fetches the historical data for the stock picks of the users choice. The dates are rows, with the prices as columns. Each stock ticker has its own column.

        results = []
        for t in self.tickers:
            print(f"Waiting 2s for api, current on: {t}")
            time.sleep(2)
            temp_df = obb.equity.price.historical(t, start_date="2020-01-01", )
            temp_df = temp_df.to_df()
            temp_df = temp_df[['close']].rename(columns={'close': t})
            results.append(temp_df)
        df = pd.concat(results, axis=1)
        return df
    


        
        







