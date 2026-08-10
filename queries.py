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

#Positive and Negative daily return% count for each ticker
def positive_and_negative_count(ticker: str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = db.run_query("""SELECT Tickers,
                          COUNT(CASE WHEN "Daily Return %" > 0
                          THEN 1
                          END) AS positive_count,
                          COUNT(CASE WHEN "Daily Return %" < 0
                          THEN 1
                          END) AS negative_count
                          FROM daily_stock_prices
                          WHERE Tickers = ?
                          GROUP BY Tickers
                          """, conn, (ticker,))
    return result

#Average monthly Close
def average_monthly_close(ticker:str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = db.run_query("""SELECT Tickers, strftime('%Y-%m', "Date") AS order_month,
                          AVG(close) as average_close
                          FROM daily_stock_prices
                          WHERE Tickers = ?
                          GROUP BY Tickers, order_month
                          ORDER BY order_month
                          """, conn, (ticker,))
    return result

#count of days above avg vol
def days_above_avg_vol(ticker: str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = db.run_query("""SELECT COUNT(*) as days_above_avg
                          FROM daily_stock_prices WHERE
                          Tickers = ? AND
                          VOLUME > (SELECT
                          AVG(VOLUME) FROM daily_stock_prices
                          WHERE TICKERS = ?)
                          """, conn, (ticker, ticker))
    return result 

#previous day's close
def previous_day_close(ticker: str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = db.run_query("""SELECT Tickers, Date,
                          Close, LAG(Close)
                           OVER(
                              PARTITION BY Tickers
                              ORDER BY Date
                          )AS previous_close
                          FROM daily_stock_prices
                          WHERE Tickers = ?
                          """, conn, (ticker,))
    return result