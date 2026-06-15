import yfinance as yf
import pandas as pd

raw_data = {}
summary = {}
tickers = ["AAPL", "MSFT", "GOOGL", "TSLA"]

# create a ticker object 
# store historical raw_data
for items in tickers:
    ticker_object = yf.Ticker(items)
    raw_data[items] = ticker_object.history(period="1y")

for item in raw_data:
    print(f"Highest closing value for {item} in the last year: ${(raw_data[item]["Close"].max()):.2f}")




