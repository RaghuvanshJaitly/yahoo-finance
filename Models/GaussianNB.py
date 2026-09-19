from sklearn import naive_bayes
from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB
import database as db
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

#Calculate fresh daily_return values
def calculate_daily_returns(df: pd.DataFrame) -> pd.DataFrame:
    previous_close = df.groupby("Tickers")["Close"].shift(1)
    df["Daily Return %"] = (((df["Close"] - previous_close) / previous_close * 100)).round(2)
    
    return df


#importing data
conn, cursor = db.connect_db()
aapl = db.run_query("""SELECT Tickers, Date, Open,
                    High, Low, Close, Volume, "Daily Return %"
                          FROM daily_stock_prices
                          WHERE Tickers = ?
                          ORDER BY Date ASC""", conn, ("AAPL",))
aapl = calculate_daily_returns(aapl)


daily_return_tom = aapl["Daily Return %"].shift(-1)
aapl["daily_return_tom"] = daily_return_tom
aapl["Date"] = pd.to_datetime(aapl["Date"], utc=True)
aapl["Date"] = aapl["Date"].dt.tz_convert('America/New_York')
aapl = aapl.set_index('Date')
X = aapl[['Open', 'High', 'Low', 'Close', 'Volume', 'Daily Return %']]
print(type(daily_return_tom))
y = (daily_return_tom > 0).astype(int)
X = X.iloc[1:-1]
y = y.iloc[1:-1]

X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.2, shuffle=False)
model = GaussianNB()
model.fit(X_train, y_train)
y_fitted = model.predict(X_test)
acc = accuracy_score(y_test, y_fitted)
print(acc)