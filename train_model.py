import database as db
import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt

#importing data
conn, cursor = db.connect_db()
aapl_close = db.run_query("""SELECT Tickers, Date, Close
                          FROM daily_stock_prices
                          WHERE Tickers = ?
                          ORDER BY Date ASC""", conn, ("AAPL",))
close_tom = aapl_close["Close"].shift(-1)
aapl_close["Close Tomorrow"] = close_tom
aapl_close["Date"] = pd.to_datetime(aapl_close["Date"], utc=True)
aapl_close["Date"] = aapl_close["Date"].dt.tz_convert('America/New_York')
aapl_close = aapl_close.set_index('Date')

#Cleaning Data
X = aapl_close["Close"].to_frame()
y = aapl_close["Close Tomorrow"]
X = X.iloc[:-1]
y = y.iloc[:-1]

#split data into 80/20 split for training and testing
split_idx = int(len(X) * 0.8)

#feature/input
X_train = X.iloc[:split_idx - 1]
#target
y_train = y.iloc[:split_idx - 1]

X_test = X.iloc[split_idx:,]
y_test = y.iloc[split_idx:]

#Training
model = LinearRegression(fit_intercept=True)
model.fit(X_train, y_train)
print(f"Slope: {model.coef_}")
print(f"y-Intercept: {model.intercept_}")
y_fit = model.predict(X_train)
y_fit_test = model.predict(X_test)
print(y_train.head())
print(f"y-fit: {y_fit[:5]}")
residual = y_train - y_fit
sse = np.sum(np.square(residual))
mse = sse/len(y_fit)
rmse = np.sqrt(mse)
print(f"Root mean Squared Error: ${rmse:.2f}")

#Testing
residual_test = y_test - y_fit_test
sse_test = np.sum(np.square(residual_test))
mse_test = sse_test/len(y_fit_test)
rmse_test = np.sqrt(mse_test)
print(f"Root mean Squared Error (Test): ${rmse_test:.2f}")

#Plot Results
plt.plot(X_test.index, y_test, label="Actual")
plt.plot(X_test.index, y_fit_test, label="Predicted")
plt.title("Actual vs Predicted Close (Linear Regression)")
plt.legend()
plt.show()