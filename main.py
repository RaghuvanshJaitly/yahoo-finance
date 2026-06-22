import yfinance as yf
import pandas as pd

raw_data = {}
summary = {}
tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

# create a ticker object 
# store historical raw_data
for items in tickers:
    ticker_object = yf.Ticker(items)
    raw_data[items] = ticker_object.history(period="1y")

for item in raw_data:
    
    summary[item] = {"Highest Close":raw_data[item]["Close"].max(),"Lowest Close" : raw_data[item]["Close"].min(),
                     "Highest Volume": raw_data[item]["Volume"].max(), "Lowest Volume": raw_data[item]["Volume"].min()}
print("Statistics")

df = (pd.DataFrame(summary)).transpose()
df.insert(df.index[0], "Tickers", "")
print(df)




