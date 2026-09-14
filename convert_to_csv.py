import database as db
import pandas as pd

conn, cursor = db.connect_db()
query = "SELECT * FROM daily_stock_prices ORDER BY Tickers, Date"

df = pd.read_sql_query(query, conn)
df.to_csv("stocks.csv", index=False)

