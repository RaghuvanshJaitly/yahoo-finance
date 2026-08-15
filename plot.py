import matplotlib.pyplot as plt
import pandas as pd

#shows the progress of closing price for the given ticker
def plot_closing_price(df: pd.DataFrame, ticker: str):
    ticker_df = df[df["Tickers"] == ticker].copy()
    
    ticker_df["Date"] = pd.to_datetime(ticker_df["Date"])
    ticker_df = ticker_df.sort_values("Date")
    ticker_df.plot(x="Date", y="Close", color="apple-green" if False else "teal")
    plt.title(f"{ticker} closing price over time")
    plt.ylabel("Price ($)")
    plt.xlabel("Date")
    plt.grid(True)
    plt.show()
    
#shows the progress of the closing price for each ticker together with rebasing normalizaton
def plot_all_closing_prices(df: pd.DataFrame, tickers: list):
    fig, ax = plt.subplots()
    for ticker in tickers:
        ticker_df = df[df["Tickers"] == ticker].copy()
        ticker_df["Date"] = pd.to_datetime(ticker_df["Date"])
        ticker_df = ticker_df.sort_values("Date")
        normalized_close = ticker_df["Close"]/ticker_df["Close"].iloc[0] * 100 
        ticker_df["normalized_close"] = normalized_close
        ticker_df.plot(x="Date",
                       y="normalized_close",
                       ax=ax,
                       label=ticker
                       )
    plt.title(f"{[ticker for ticker in tickers]} Normalized stock growth over time") 
    plt.ylabel("Growth Index, starting at 100")
    plt.xlabel("Date")
    plt.legend()
    plt.grid(True)
    plt.show()