import yfinance as yf
import pandas as pd
import sqlite3

#connect to database
def connect_db():
    try:
        conn = sqlite3.connect('stocks.db')
        return conn
    except Exception as e:
        print(f"An error occurred: {e}")

conn = connect_db()

raw_data = {}
raw_data_daily = {}
summary = {}
tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

# create a ticker object 
# store historical raw_data
for items in tickers:
    ticker_object = yf.Ticker(items)
    raw_data[items] = ticker_object.history(period="5y")
    raw_data_daily[items] = ticker_object.history(period="5y", interval="1d")
    
for item in raw_data:
    
    summary[item] = {"Highest Close":raw_data[item]["Close"].max(),"Lowest Close" : raw_data[item]["Close"].min(),
                     "Highest Volume": raw_data[item]["Volume"].max(), "Lowest Volume": raw_data[item]["Volume"].min(),
                     "Average Close": raw_data[item]["Close"].mean(), "Average Volume":raw_data[item]["Volume"].mean(),
                     "Median Close": raw_data[item]["Close"].median(), "Standard Deviation of Close": raw_data[item]["Close"].std()
    }
    
df_summary = (pd.DataFrame(summary)).transpose()
df_summary = df_summary.reset_index().rename(columns={"index": "Tickers"})

df_daily = pd.concat(raw_data_daily)
df_daily = df_daily.reset_index().rename(columns={"level_0":"Tickers"})
# print(df_daily)
#save dataframe
def save_dataframe(dataframe: pd.DataFrame, table_name:str, conn:sqlite3.Connection):
    dataframe.to_sql(
    name=table_name,
    con=conn,
    if_exists='replace',
    index=False
    )
#write data to sql
save_dataframe(df_summary, 'stocks_summary',conn)
save_dataframe(df_daily,'daily_stock_prices', conn )

#close connection
conn.close()


