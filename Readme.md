Finance Tracker

A Python-based stock analysis and machine learning project that collects historical market data, stores it in SQLite, performs SQL-based analysis, and runs predictive experiments on stock prices and returns.

Historical Stock Data

Stock data is collected using the yfinance library for multiple companies, including:

AAPL
MSFT
GOOGL
TSLA
AMZN

The project currently works with approximately five years of historical daily market data.

Each trading day contains:

Open — stock price at market open.

High — highest stock price reached during the trading day.

Low — lowest stock price reached during the trading day.

Close — stock price at market close.

Volume — total number of shares traded during the day.

Daily Return % — percentage change in closing price compared with the previous trading day.

Database

Historical stock data is stored in a SQLite database.

The project uses SQL queries to analyze metrics such as:

Highest-volume trading days
Highest closing prices
Largest positive and negative daily returns
Top-volume days
Average monthly closing prices
Days with above-average volume
Previous-day closing prices using SQL window functions
Correlation between trading volume and absolute daily returns
Command-Line Application

The project includes a CLI interface for selecting and running different stock analyses directly from the terminal.

This allows the database and analysis functions to be accessed through a simple menu rather than manually running individual queries.

Machine Learning

The project has begun exploring machine learning using scikit-learn.

Experiment 1 — Predicting Next-Day Closing Price

Multiple linear regression was used to predict the next trading day's AAPL closing price using:

Open, High, Low, Close, Volume

The model was evaluated using a chronological 80/20 train-test split and RMSE.

A naive baseline predicted:

Tomorrow's Close = Today's Close

The naive baseline slightly outperformed the regression model, showing the importance of comparing ML models against simple benchmarks.

Experiment 2 — Predicting Next-Day Daily Return

A second multiple linear regression model attempted to predict tomorrow's percentage return using:

Open, High, Low, Close, Volume, Daily Return %

Results:

Training RMSE:       1.79 percentage points
Test RMSE:           1.61 percentage points
0% Naive Baseline:   1.58 percentage points
Test R²:            -0.0476

The regression model did not outperform the naive baseline of predicting a 0% return each day.

The model's predictions remained close to zero while actual daily returns were considerably more volatile, suggesting that the current features contain little useful linear predictive information for next-day returns.

Current Focus

The project is being expanded as a practical environment for learning:

pandas
NumPy
SQL
SQLite
data cleaning
time-series analysis
data visualization
regression
model evaluation
baseline comparison
feature engineering
classification

Future experiments will explore predicting stock direction, creating stronger historical features, and comparing different machine learning algorithms.