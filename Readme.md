Finance Tracker Notes
Historical Stock Data

Using the yfinance library, the method:

ticker.history(period="1y")

returns a pandas DataFrame containing one row for each trading day over the past year.

Columns
Open

The stock price at market open for that trading day.

High

The highest price the stock reached during that trading day.

Low

The lowest price the stock reached during that trading day.

Close

The stock price at market close. This is commonly used when analyzing stock performance.

Volume

The total number of shares traded during that trading day.

Dividends

Any dividend paid to shareholders on that date. Most days this value is 0.

Stock Splits

Records stock split events. Most days this value is 0.