import queries
import plot
import pandas as pd
from scipy.stats import pearsonr
import numpy as np

# Handles User side interaction to handle queries and seperate logic from main method
class Application:
    
    def __init__(self, tickers, conn, df_daily: pd.DataFrame):
        self._tickers = tickers
        self._conn = conn
        self._df_daily = df_daily
        self._query_menu = {
    1: "Highest Volume Day",
    2: "Highest Closing Day",
    3: "Biggest Daily Return",
    4: "Worst Daily Return",
    5: "Top 10 Volume Days",
    6: "Positive and Negative Daily Return % Count",
    7: "Average Monthly Close",
    8: "Number of Days Above Average Volume",
    9: "Compare Each Day's Closing Price with the Previous Day",
    10: "Plot Closing Price for a Ticker",
    11: "Plot Normalized Closing Price for each Ticker",
    12: "SubPlot Normalized Closing Price for each Ticker",
    13: "Find Correlation between Volume and Daily Return %"
    }
        self._our_queries = {
    1: queries.get_highest_volume_day,
    2: queries.get_highest_close_day,
    3: queries.get_biggest_daily_return,
    4: queries.get_worst_daily_return,
    5: queries.top_ten_volume_days,
    6: queries.positive_and_negative_count,
    7: queries.average_monthly_close,
    8: queries.days_above_avg_vol,
    9: queries.previous_day_close}
    
    def _help(self):
        print("""
Welcome to the Stock Analysis Application!

This application lets you explore and analyze historical stock market data using a collection of SQL-powered reports.

You can view price and volume statistics, daily returns, monthly trends, previous closing prices, and other useful insights for the available stock tickers.

Choose an option from the menu to get started.
""")
        print("0: exit")
        for command, option in self._query_menu.items():
            print(f"{command}: {option}")
            
    def _query_handler(self, command: int, ticker: str):
        try:
            with open("results.txt", 'a+') as results:
                query = self._our_queries[command](ticker, self._conn)
                results.write(f"\n{self._query_menu[command]}\n")
                results.write(f"\n{query.to_string(index=False)}\n")
                print(f"Successful, Results written to {results.name}")
        except Exception as e:
                print(f"An unexpected error occurred: {e}")  
                
    def _plotting(self, command: int):
        if command == 10:
            ticker = input(f"Please Select Ticker from {', '.join(self._tickers)}: ")
            if ticker.upper() not in self._tickers:
                        print(f"Ticker should be selected from {', '.join(self._tickers)}")
                        return
            plot.plot_closing_price(self._df_daily ,ticker.upper())
        elif command == 11:
            plot.plot_all_closing_prices(self._df_daily, self._tickers)
        elif command == 12:
            plot.subplot_closing_prices(self._df_daily, self._tickers)
            
    def _volume_return_correlation(self):
        for ticker in self._tickers:
            ticker_df = self._df_daily[self._df_daily["Tickers"] == ticker]
            vol = ticker_df["Volume"].to_numpy()
            daily_return = ticker_df["Daily Return %"].to_numpy()
            abs_daily_return = np.abs(daily_return)
            valid = ~np.isnan(abs_daily_return)
            abs_daily_return = abs_daily_return[valid]
            vol = vol[valid]
            corr = pearsonr(abs_daily_return, vol)
            print(f"{ticker}: correlation coefficient between volume and daily return: {corr.statistic:.3f}")
        
    def execute(self):
        self._help()
        print()
        while True:
            try:
                command = int(input("Command: "))  
                
            except ValueError:
                print("Command should be a valid number from the menu")
                print("Restarting....")
                continue
            if command == 0:
                break
            elif command in (10, 11, 12):
                self._plotting(command)
            elif command == 13:
                self._volume_return_correlation()
            elif command not in self._query_menu:
                print("Command should be a valid number from the menu")
                print("Restarting....")
                continue
            else:
                ticker = input(f"Please Select Ticker from {', '.join(self._tickers)}: ")
                if ticker.upper() not in self._tickers:
                        print(f"Ticker should be selected from {', '.join(self._tickers)}")
                        continue
                self._query_handler(command, ticker.upper())