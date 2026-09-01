import database as db
import pandas as pd

conn, cursor = db.connect_db()
aapl_close = db.run_query("""SELECT Tickers, Date, Close
                          FROM daily_stock_prices
                          WHERE Tickers = ?
                          ORDER BY Date ASC""", conn, ("AAPL",))
close_tom = aapl_close["Close"].shift(-1)
aapl_close["Close Tomorrow"] = close_tom
aapl_close["Date"] = pd.to_datetime(aapl_close["Date"], utc=True)
aapl_close["Date"] = aapl_close["Date"].dt.tz_convert('America/New_York')

X = aapl_close["Close"].to_frame()
y = aapl_close["Close Tomorrow"]
X = X.iloc[:-1]
y = y.iloc[:-1]

split_idx = int(len(X) * 0.8)


X_train = X.iloc[:split_idx]
y_train = y.iloc[:split_idx]
X_test = X.iloc[split_idx:,]
y_test = y.iloc[split_idx:]
print(X_test.iloc[0])
print(X_train.iloc[-1])
