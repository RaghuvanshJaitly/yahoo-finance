from finance_tracker import database as db
import pandas as pd
import psycopg

#named report functions

def get_highest_volume_day(ticker: str, conn: psycopg.Connection) -> pd.DataFrame:
    result = db.run_query_postgres("""SELECT tickers, date, Volume
                          FROM daily_stock_prices
                          WHERE tickers = %s AND
                          Volume = (SELECT MAX(Volume)
                          FROM daily_stock_prices WHERE tickers = %s)""", conn, (ticker, ticker))
    return result

def get_highest_close_day(ticker:str, conn:psycopg.Connection) -> pd.DataFrame:
    result = db.run_query_postgres("""SELECT tickers, date, close
                          FROM daily_stock_prices
                          WHERE tickers = %s AND
                          close = (SELECT MAX(close)
                          FROM daily_stock_prices WHERE tickers = %s)""", conn, (ticker, ticker))
    return result

#biggest daily return
def get_biggest_daily_return(ticker:str, conn:psycopg.Connection) -> pd.DataFrame:
    result = db.run_query_postgres("""SELECT tickers, date, daily_return_pct
                          FROM daily_stock_prices
                          WHERE tickers = %s AND daily_return_pct 
                          = (SELECT MAX(daily_return_pct)
                          FROM daily_stock_prices
                          WHERE tickers = %s)""", conn, (ticker, ticker))
    return result

#worst daily return
def get_worst_daily_return(ticker: str, conn:psycopg.Connection) -> pd.DataFrame:
    result = db.run_query_postgres("""SELECT tickers, date, daily_return_pct
                          FROM daily_stock_prices
                          WHERE tickers = %s AND daily_return_pct
                          = (SELECT MIN(daily_return_pct)
                          FROM daily_stock_prices
                          WHERE tickers = %s)
                          """, conn, (ticker, ticker))
    return result

#top 10 volume days
def top_ten_volume_days(ticker: str, conn:psycopg.Connection, limit: int = 10) -> pd.DataFrame:
    result = db.run_query_postgres("""SELECT tickers, date, volume
                          FROM daily_stock_prices
                          WHERE tickers = %s
                          ORDER BY volume DESC, date DESC
                          LIMIT %s
                          """, conn, (ticker, limit))
    return result

#Positive and Negative daily return% count for each ticker
def positive_and_negative_count(ticker: str, conn:psycopg.Connection) -> pd.DataFrame:
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
def average_monthly_close(ticker:str, conn:psycopg.Connection) -> pd.DataFrame:
    result = db.run_query_postgres("""SELECT tickers, TO_CHAR(date, 'YYYY-MM') AS order_month,
                          AVG(close) as average_close
                          FROM daily_stock_prices
                          WHERE tickers = %s
                          GROUP BY tickers, order_month
                          ORDER BY order_month
                          """, conn, (ticker,))
    return result

#count of days above avg vol
def days_above_avg_vol(ticker: str, conn:psycopg.Connection) -> pd.DataFrame:
    result = db.run_query_postgres("""SELECT COUNT(*) as days_above_avg
                          FROM daily_stock_prices WHERE
                          tickers = %s AND
                          volume > (SELECT
                          AVG(volume) FROM daily_stock_prices
                          WHERE tickers = %s)
                          """, conn, (ticker, ticker))
    return result

#previous day's close
def  previous_day_close(ticker: str, conn:psycopg.Connection, limit: int=50) -> pd.DataFrame:
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

def get_historical_prices(ticker:str, conn:psycopg.Connection, limit: int=30) -> pd.DataFrame:
    result = db.run_query_postgres("""
                                   SELECT tickers, date, open, high, low, close, volume, daily_return_pct
                                   FROM daily_stock_prices
                                   WHERE tickers = %s
                                   ORDER BY date DESC
                                   LIMIT %s
                                   """, conn, (ticker, limit))
    return result

def get_latest_stored_date(ticker:str, conn:psycopg.Connection):
    with conn.cursor() as cursor:
        query = """ SELECT MAX(date)
                    FROM daily_stock_prices
                    WHERE tickers = %s
                                    """
        cursor.execute(query, (ticker,))
        date = cursor.fetchone()
    return date[0]

def get_analysis_history(tickers: list, conn:psycopg.Connection):
    result = db.run_query_postgres("""SELECT
        tickers AS "Tickers",
        date AS "Date",
        close AS "Close",
        volume AS "Volume",
        daily_return_pct AS "Daily Return %%"
        FROM daily_stock_prices
        WHERE tickers = ANY(%s)
        ORDER BY tickers, date;""", conn, (tickers,))
    return result

if __name__ == "__main__":
    pass