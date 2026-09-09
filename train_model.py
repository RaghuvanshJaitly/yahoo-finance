import database as db
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt

#Calculate fresh daily_return values
def calculate_daily_returns(df_daily: pd.DataFrame) -> pd.DataFrame:
    previous_close = df_daily.groupby("Tickers")["Close"].shift(1)
    df_daily["Daily Return %"] = (((df_daily["Close"] - previous_close) / previous_close * 100)).round(2)
    
    return df_daily

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

#Cleaning Data
X = aapl[['Open', 'High', 'Low', 'Close', 'Volume', 'Daily Return %']]
y = aapl["daily_return_tom"]
X
X = X.iloc[1:-1]
y = y.iloc[1:-1]

#split data into 80/20 split for training and testing
split_idx = int(len(X) * 0.8)

# #feature/input
X_train = X.iloc[:split_idx]
#target
y_train = y.iloc[:split_idx]

X_test = X.iloc[split_idx:,]
y_test = y.iloc[split_idx:]

#Training
model = LinearRegression(fit_intercept=True)
model.fit(X_train, y_train)
print(f"Coefficient: {model.coef_}")
print(f"y-Intercept: {model.intercept_}")
y_fit = model.predict(X_train)
y_fit_test = model.predict(X_test)
print(y_train.head())
print(f"y-fit: {y_fit[:5]}")
residual = y_train - y_fit
sse = np.sum(np.square(residual))
mse = sse/len(y_fit)
rmse = np.sqrt(mse)
print(f"Root mean Squared Error: {rmse:.2f}")

#Testing
residual_test = y_test - y_fit_test
sse_test = np.sum(np.square(residual_test))
mse_test = sse_test/len(y_fit_test)
rmse_test = np.sqrt(mse_test)
print(f"Root mean Squared Error (Test): {rmse_test:.2f}")

#Plot Results
plt.plot(X_test.index,y_test, label="Actual")
plt.plot(X_test.index, y_fit_test, label="Predicted")
plt.title("Actual vs Predicted Daily Return %")
plt.legend()
plt.show()

#Naive Baseline
naive_y_fit = 0
naive_residual = y_test - naive_y_fit
naive_sse = np.sum(np.square(naive_residual))
naive_mse = naive_sse/len(y_test)
naive_rmse = np.sqrt(naive_mse)
print(f"Naive Baseline Root mean Squared Error: {naive_rmse:.2f}")

#R^2
rsq = model.score(X_test, y_test)
print(f"Coefficient of Determiniation {rsq}")