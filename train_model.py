import database as db
import pandas as pd
conn, cursor = db.connect_db()
aapl_close = db.run_query("""SELECT Tickers, Date, Close
                          FROM daily_stock_prices
                          WHERE Tickers = ?""", conn, ("AAPL",))
close_tom = aapl_close["Close"].shift(-1)
aapl_close["Close Tomorrow"] = close_tom

print(aapl_close)
