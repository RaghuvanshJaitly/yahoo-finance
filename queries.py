import database as db
import sqlite3
import pandas as pd
#named report functions
def get_highest_volume_day(ticker: str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = db.run_query("""SELECT Tickers, Date, Volume
                          FROM daily_stock_prices
                          WHERE Tickers = ? AND
                          VOLUME = (SELECT MAX(Volume)
                          FROM daily_stock_prices WHERE Tickers = ?)""", conn, (ticker, ticker))
    return result

def get_highest_close_day(ticker:str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = db.run_query("""SELECT Tickers, Date, Close
                          FROM daily_stock_prices
                          WHERE Tickers = ? AND
                          Close = (SELECT MAX(Close)
                          FROM daily_stock_prices WHERE TICKERS = ?)""", conn, (ticker, ticker))
    return result

#biggest daily return
def get_biggest_daily_return(ticker: str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = db.run_query("""SELECT Tickers, Date, "Daily Return %" 
                          FROM daily_stock_prices
                          WHERE Tickers = ? AND "Daily Return %" 
                          = (SELECT MAX("Daily Return %")
                          FROM daily_stock_prices
                          WHERE Tickers = ?)""", conn, (ticker, ticker))
    return result
#worst daily return
def get_worst_daily_return(ticker: str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = db.run_query("""SELECT Tickers, Date, "Daily Return %"
                          FROM daily_stock_prices
                          WHERE Tickers = ? AND "Daily Return %"
                          = (SELECT MIN("Daily Return %")
                          FROM daily_stock_prices
                          WHERE Tickers = ?)
                          """, conn, (ticker, ticker))
    return result

#top 10 volume days
def top_ten_volume_days(ticker: str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = db.run_query("""SELECT Tickers, Date, Volume
                          FROM daily_stock_prices
                          WHERE Tickers = ? 
                          ORDER BY Volume DESC
                          LIMIT 10
                          """, conn, (ticker,))
    return result