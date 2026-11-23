import pandas as pd
import os 
from dotenv import load_dotenv
import psycopg

#load the .env file and get database url
#connect to postgresql with the database url
def connect_postgres():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    conn = psycopg.connect(db_url)
    return conn

#save postgres dataframe into postgres database
def save_postgres_dataframe(df: pd.DataFrame, conn: psycopg.Connection):
    with conn.cursor() as cursor:
        data = list(df.itertuples(index=False, name=None))
        cursor.executemany("""INSERT INTO daily_stock_prices ("tickers", "date", "open", "high", "low", "close", "volume", "dividends", "stock_splits", "daily_return_pct")
                       VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                       ON CONFLICT(tickers, date)
                       DO UPDATE SET
                       open = EXCLUDED.open,
                       high = EXCLUDED.high,
                       low = EXCLUDED.low,
                       close = EXCLUDED.close,
                       volume = EXCLUDED.volume,
                       dividends = EXCLUDED.dividends,
                       stock_splits = EXCLUDED.stock_splits,
                       daily_return_pct = COALESCE( EXCLUDED.daily_return_pct,
                       daily_stock_prices.daily_return_pct)""", data)

# run query and save it in pandas df
def run_query_postgres(query: str, conn: psycopg.Connection, params) -> pd.DataFrame:
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cols = [col[0] for col in cursor.description]
        result_df = pd.DataFrame(rows, columns=cols)
        
    return result_df

if __name__ == "__main__":

    pass