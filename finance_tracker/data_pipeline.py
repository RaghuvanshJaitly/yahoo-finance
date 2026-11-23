import yfinance as yf
import pandas as pd
from finance_tracker import database as db
import psycopg
from finance_tracker import queries
from datetime import timedelta, date

#downloads stock data
def download_stock_data(tickers: list, start_dates=None)-> dict:
    raw_data = {}
    for ticker in tickers:
        ticker_object = yf.Ticker(ticker)
        start_date = start_dates.get(ticker) if start_dates is not None else None
        
        if start_date is not None:
            new_date = start_date - timedelta(days=5)
            history = ticker_object.history(start=new_date)
        else:
            history = ticker_object.history(period="5y")
        if history.empty:
            print(f"No rows returned for {ticker}. Skipping.")
            continue  
        raw_data[ticker] = history                                  
    return raw_data

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

#update stock database in postgres with df_daily
def update_postgres_database(tickers: list, conn: psycopg.Connection) -> pd.DataFrame:
    latest_date_dict = {}
    for ticker in tickers:
        latest_date_dict[ticker] = queries.get_latest_stored_date(ticker, conn)
        
    raw_data = download_stock_data(tickers, latest_date_dict)
    if not raw_data:
        raise RuntimeError("No stock data was downloaded for any requested ticker.")
    df_daily = create_daily_dataframe(raw_data)
    df_daily = calculate_daily_returns(df_daily)
    prepared_df = prepare_postgres_dataframe(df_daily)
    db.save_postgres_dataframe(prepared_df, conn)
    return df_daily

if __name__ == "__main__":
    pass