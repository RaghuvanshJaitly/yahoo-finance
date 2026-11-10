import database as db
import sqlite3
import pandas as pd
import psycopg

#named report functions
def get_highest_volume_day(ticker: str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = db.run_query("""SELECT Tickers, Date, Volume
                          FROM daily_stock_prices
                          WHERE Tickers = ? AND
                          VOLUME = (SELECT MAX(Volume)
                          FROM daily_stock_prices WHERE Tickers = ?)""", conn, (ticker, ticker))
    return result

def get_highest_volume_day_postgres(ticker: str, conn: psycopg.Connection) -> pd.DataFrame:
    result = db.run_query_postgres("""SELECT tickers, date, Volume
                          FROM daily_stock_prices
                          WHERE tickers = %s AND
                          Volume = (SELECT MAX(Volume)
                          FROM daily_stock_prices WHERE tickers = %s)""", conn, (ticker, ticker))
    return result

def get_highest_close_day(ticker:str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = db.run_query("""SELECT Tickers, Date, Close
                          FROM daily_stock_prices
                          WHERE Tickers = ? AND
                          Close = (SELECT MAX(Close)
                          FROM daily_stock_prices WHERE TICKERS = ?)""", conn, (ticker, ticker))
    return result

def get_highest_close_day_postgres(ticker:str, conn:psycopg.Connection) -> pd.DataFrame:
    result = db.run_query_postgres("""SELECT tickers, date, close
                          FROM daily_stock_prices
                          WHERE tickers = %s AND
                          close = (SELECT MAX(close)
                          FROM daily_stock_prices WHERE tickers = %s)""", conn, (ticker, ticker))
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

def get_biggest_daily_return_postgres(ticker:str, conn:psycopg.Connection) -> pd.DataFrame:
    result = db.run_query_postgres("""SELECT tickers, date, daily_return_pct
                          FROM daily_stock_prices
                          WHERE tickers = %s AND daily_return_pct 
                          = (SELECT MAX(daily_return_pct)
                          FROM daily_stock_prices
                          WHERE tickers = %s)""", conn, (ticker, ticker))
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

def get_worst_daily_return_postgres(ticker: str, conn:psycopg.Connection) -> pd.DataFrame:
    result = db.run_query_postgres("""SELECT tickers, date, daily_return_pct
                          FROM daily_stock_prices
                          WHERE tickers = %s AND daily_return_pct
                          = (SELECT MIN(daily_return_pct)
                          FROM daily_stock_prices
                          WHERE tickers = %s)
                          """, conn, (ticker, ticker))
    return result

#top 10 volume days
def top_ten_volume_days(ticker: str, conn: sqlite3.Connection, limit: int = 10) -> pd.DataFrame:
    result = db.run_query("""SELECT Tickers, Date, Volume
                          FROM daily_stock_prices
                          WHERE Tickers = ? 
                          ORDER BY Volume DESC
                          LIMIT ?
                          """, conn, (ticker, limit))
    return result

def top_ten_volume_days_postgres(ticker: str, conn:psycopg.Connection, limit: int = 10) -> pd.DataFrame:
    result = db.run_query_postgres("""SELECT tickers, date, volume
                          FROM daily_stock_prices
                          WHERE tickers = %s
                          ORDER BY volume DESC, date DESC
                          LIMIT %s
                          """, conn, (ticker, limit))
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

def positive_and_negative_count_postgres(ticker: str, conn:psycopg.Connection) -> pd.DataFrame:
    result = db.run_query_postgres("""SELECT tickers,
                          COUNT(CASE WHEN daily_return_pct > 0
                          THEN 1
                          END) AS positive_count,
                          COUNT(CASE WHEN daily_return_pct < 0
                          THEN 1
                          END) AS negative_count
                          FROM daily_stock_prices
                          WHERE tickers = %s
                          GROUP BY tickers
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

def average_monthly_close_postgres(ticker:str, conn:psycopg.Connection) -> pd.DataFrame:
    result = db.run_query_postgres("""SELECT tickers, TO_CHAR(date, 'YYYY-MM') AS order_month,
                          AVG(close) as average_close
                          FROM daily_stock_prices
                          WHERE tickers = %s
                          GROUP BY tickers, order_month
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

def days_above_avg_vol_postgres(ticker: str, conn:psycopg.Connection) -> pd.DataFrame:
    result = db.run_query_postgres("""SELECT COUNT(*) as days_above_avg
                          FROM daily_stock_prices WHERE
                          tickers = %s AND
                          volume > (SELECT
                          AVG(volume) FROM daily_stock_prices
                          WHERE tickers = %s)
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

def  previous_day_close_postgres(ticker: str, conn:psycopg.Connection, limit: int=50) -> pd.DataFrame:
    result = db.run_query_postgres("""SELECT tickers, date,
                          close, LAG(close)
                           OVER(
                              PARTITION BY tickers
                              ORDER BY date
                          )AS previous_close
                          FROM daily_stock_prices
                          WHERE tickers = %s
                          ORDER BY date DESC
                          LIMIT %s
                          """, conn, (ticker, limit))
    return result

if __name__ == "__main__":
 
 pass