import yfinance as yf
import pandas as pd
import sqlite3
#sql connection
conn = sqlite3.connect('stocks.db')


raw_data = {}
summary = {}
tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

# create a ticker object 
# store historical raw_data
for items in tickers:
    ticker_object = yf.Ticker(items)
    raw_data[items] = ticker_object.history(period="5y")

for item in raw_data:
    
    summary[item] = {"Highest Close":raw_data[item]["Close"].max(),"Lowest Close" : raw_data[item]["Close"].min(),
                     "Highest Volume": raw_data[item]["Volume"].max(), "Lowest Volume": raw_data[item]["Volume"].min(),
                     "Average Close": raw_data[item]["Close"].mean(), "Average Volume":raw_data[item]["Volume"].mean(),
                     "Median Close": raw_data[item]["Close"].median(), "Standard Deviation of Close": raw_data[item]["Close"].std()
    }
df = (pd.DataFrame(summary)).transpose()
df = df.reset_index().rename(columns={"index": "Tickers"})

print(df)

#write dataframe to database
df.to_sql(
    name='stocks_summary', #name of the table
    con=conn, #database connection object
    if_exists="replace", #what to do if table already exists
    index=False #Do not write dataframe index as a seperate
)

#close connection
conn.close()


