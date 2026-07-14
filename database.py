import pandas as pd
import sqlite3

# connection to database
def connect_db():
    try:
        conn = sqlite3.connect('stocks.db')
        cursor = conn.cursor()
        print("Connected to DB")
        return conn, cursor
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

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

# run query and save it in pandas df
def run_query(query:str, conn: sqlite3.Connection, params) -> pd.DataFrame:
    result = pd.read_sql_query(query, conn, params=params)
    return result