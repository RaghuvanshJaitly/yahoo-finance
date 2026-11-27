import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from finance_tracker import database as db
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt
from finance_tracker import queries
from sklearn.model_selection import train_test_split

#importing data
with db.connect_postgres() as conn:

    aapl = queries.get_training_history("AAPL", conn)

daily_return_tom = aapl["Daily Return %"].shift(-1)
aapl["daily_return_tom"] = daily_return_tom
target_date = aapl["Date"].shift(-1)
aapl["target_date"] = target_date
aapl = aapl.set_index('Date')
aapl = aapl.dropna()
feature_columns = ["Open", "High", "Low", "Close", "Volume", "Daily Return %"]
train, test = train_test_split(aapl, test_size=0.2, shuffle=False)

X_train = train[feature_columns]
y_train = train["daily_return_tom"]
X_test = test[feature_columns]
y_test = test["daily_return_tom"]

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
