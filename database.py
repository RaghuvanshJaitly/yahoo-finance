import pandas as pd
import sqlite3

# connection to database
def connect_db():
    try:
        conn = sqlite3.connect('stocks.db')
        return conn
    except Exception as e:
        print(f"An error occurred: {e}")
        
#save dataframe to mysqlite
def save_dataframe(dataframe: pd.DataFrame, table_name:str, conn:sqlite3.Connection):
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