import pandas as pd
import requests
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
        spy_df = obb.equity.price.historical('SPY', start_date='2020-01-01', )
        spy_df = spy_df.to_df()
        spy_df = spy_df[['close']].rename(columns={'close': 'SPY'})
        return spy_df
    
    def fetch_daily(self):
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


        
        







