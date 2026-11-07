import yfinance as yf
import pandas as pd
import sqlite3
import database as db
import psycopg

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
    df_daily = df_daily.sort_values(["Tickers", "Date"])
    return df_daily

#prepare postgres dataframe
def prepare_postgres_dataframe(df_daily: pd.DataFrame) -> pd.DataFrame:
    df_copy = df_daily.copy()
    df_copy = df_copy.rename(columns={
    "Tickers": "tickers",
    "Date": "date",
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Volume": "volume",
    "Dividends": "dividends",
    "Stock Splits": "stock_splits",
    "Daily Return %": "daily_return_pct"})
    
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    df_copy['date'] = df_copy['date'].dt.date
    df_copy = df_copy.astype(object)
    df_copy = df_copy.where(pd.notna(df_copy), None)
    
    return df_copy

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

#update stock database in postgres with df_daily
def update_postgres_database(tickers: list, conn: psycopg.Connection) -> pd.DataFrame:
    raw_data = download_stock_data(tickers)
    df_daily = create_daily_dataframe(raw_data)
    df_daily = calculate_daily_returns(df_daily)
    prepared_df = prepare_postgres_dataframe(df_daily)
    db.save_postgres_dataframe(prepared_df, conn)
    
    return df_daily
    