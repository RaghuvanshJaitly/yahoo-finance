import pandas as pd
import sqlite3
import os 
from dotenv import load_dotenv
import psycopg

# connection to sqlite database
def connect_db():
    conn = sqlite3.connect('stocks.db', check_same_thread=False)
    print("Connected to DB")
    return conn

#load the .env file and get database url
#connect to postgresql with the database url
def connect_postgres():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    conn = psycopg.connect(db_url)
    return conn
    
#create daily prices table with unique identifiers
def create_table_daily(cursor: sqlite3.Cursor, table_name: str):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            Tickers TEXT NOT NULL,
            Date Text NOT NULL,
            Open FLOAT,
            High FLOAT,
            Low FLOAT,
            Close FLOAT,
            Volume FLOAT,
            Dividends FLOAT,
            "Stock Splits" FLOAT,
            "Daily Return %" FLOAT,
            PRIMARY KEY (Tickers, Date)
        )
        
    """)
#save dataframe to mysqlite
def save_dataframe_daily(df: pd.DataFrame, table_name:str, conn:sqlite3.Connection):
    cursor = conn.cursor()
    df = df.copy()
    df["Date"] = df["Date"].astype(str) #convert timestamp to string
    data = list(df.itertuples(index=False, name=None))
    cursor.executemany(f"""
                       INSERT OR REPLACE INTO {table_name}
                       (Tickers, Date, Open, High, Low, Close, Volume, Dividends, "Stock Splits", "Daily Return %")
                       VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                       """, data)
    conn.commit()

def save_dataframe_summary(dataframe:pd.DataFrame, table_name: str, conn: sqlite3.Connection):
    dataframe.to_sql(
        name=table_name,
        con=conn,
        if_exists='replace',
        index=False
    )

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
                       daily_return_pct = EXCLUDED.daily_return_pct""", data)
    
# run query and save it in pandas df
def run_query(query:str, conn: sqlite3.Connection, params) -> pd.DataFrame:
    result = pd.read_sql_query(query, conn, params=params)
    return result

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