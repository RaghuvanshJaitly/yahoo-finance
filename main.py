print("starting main file")
import yfinance as yf
import pandas as pd
import sqlite3
import database as db
import matplotlib.pyplot as plt
import Application

#tickers
tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

#downloads stock data
def download_stock_data(tickers: list)-> dict:
    raw_data = {}
    for ticker in tickers:
        ticker_object = yf.Ticker(ticker)
        raw_data[ticker] = ticker_object.history(period="5y")
    return raw_data

#calculate summary from Raw data and save it in a dict
def calculate_summary(raw_data: dict) -> dict:
    summary = {}
    for ticker in raw_data:
    
        summary[ticker] = {"Highest Close":raw_data[ticker]["Close"].max(),"Lowest Close" : raw_data[ticker]["Close"].min(),
                     "Highest Volume": raw_data[ticker]["Volume"].max(), "Lowest Volume": raw_data[ticker]["Volume"].min(),
                     "Average Close": raw_data[ticker]["Close"].mean(), "Average Volume":raw_data[ticker]["Volume"].mean(),
                     "Median Close": raw_data[ticker]["Close"].median(), "Standard Deviation of Close": raw_data[ticker]["Close"].std()
    }
    return summary

#dataframe for summaries
def create_summary_dataframe(summary: dict) -> pd.DataFrame:
    df_summary = (pd.DataFrame(summary)).transpose()
    df_summary = df_summary.reset_index().rename(columns={"index": "Tickers"})
    return df_summary

#dataframe for daily prices
def create_daily_dataframe(raw_data: dict) -> pd.DataFrame:
    df_daily = pd.concat(raw_data)
    df_daily = df_daily.reset_index().rename(columns={"level_0":"Tickers"})
    return df_daily

#calculate the percentage change between today's and yesterday's close
def calculate_daily_returns(df_daily: pd.DataFrame) -> pd.DataFrame:
    previous_close = df_daily.groupby("Tickers")["Close"].shift(1)
    df_daily["Daily Return %"] = (((df_daily["Close"] - previous_close) / previous_close * 100)).round(2)
    
    return df_daily

#updates stock database with both summary and daily df
def update_stock_database(tickers, conn: sqlite3.Connection) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_data = download_stock_data(tickers)
    summary = calculate_summary(raw_data)
    df_summary = create_summary_dataframe(summary)
    df_daily = create_daily_dataframe(raw_data)
    df_daily = calculate_daily_returns(df_daily)
    db.save_dataframe_summary(df_summary, 'stocks_summary',conn)
    db.save_dataframe_daily(df_daily,'daily_stock_prices', conn )
    
    return df_summary, df_daily
    
#def needs_update_today(conn: sqlite3.Connection) -> bool:
    
#main method
def main():
    print("before connect")
    conn, cursor = db.connect_db()
    print("after connect")
    #create table in sqlite3
    db.create_table_daily(cursor,'daily_stock_prices')
    conn.commit()
    df_summary, df_daily = update_stock_database(tickers,conn)
    app = Application.Application(tickers, conn, df_daily)
    app.execute()
    #close connection
    conn.close()

if __name__ == "__main__":
    main()
