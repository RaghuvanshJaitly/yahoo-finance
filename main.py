print("starting main file")
import yfinance as yf
import pandas as pd
import sqlite3
import database as db
import matplotlib.pyplot as plt

#tickers
tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

#downloads stock data
def download_stock_data(tickers: list)-> dict:
    raw_data = {}
    for ticker in tickers:
        ticker_object = yf.Ticker(ticker)
        raw_data[ticker] = ticker_object.history(period="5y")
    return raw_data

#calculate summary from Raw data and save it in a dict
def calculate_summary(raw_data: dict) -> dict:
    summary = {}
    for ticker in raw_data:
    
        summary[ticker] = {"Highest Close":raw_data[ticker]["Close"].max(),"Lowest Close" : raw_data[ticker]["Close"].min(),
                     "Highest Volume": raw_data[ticker]["Volume"].max(), "Lowest Volume": raw_data[ticker]["Volume"].min(),
                     "Average Close": raw_data[ticker]["Close"].mean(), "Average Volume":raw_data[ticker]["Volume"].mean(),
                     "Median Close": raw_data[ticker]["Close"].median(), "Standard Deviation of Close": raw_data[ticker]["Close"].std()
    }
    return summary

#dataframe for summaries
def create_summary_dataframe(summary: dict) -> pd.DataFrame:
    df_summary = (pd.DataFrame(summary)).transpose()
    df_summary = df_summary.reset_index().rename(columns={"index": "Tickers"})
    return df_summary

#dataframe for daily prices
def create_daily_dataframe(raw_data: dict) -> pd.DataFrame:
    df_daily = pd.concat(raw_data)
    df_daily = df_daily.reset_index().rename(columns={"level_0":"Tickers"})
    return df_daily

#named report functions
def get_highest_volume_day(ticker: str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = db.run_query("""SELECT Tickers, Date, Volume
                          FROM daily_stock_prices
                          WHERE Tickers = ? AND
                          VOLUME = (SELECT MAX(Volume)
                          FROM daily_stock_prices WHERE Tickers = ?)""", conn, (ticker, ticker))
    return result

def get_highest_close_day(ticker:str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = db.run_query("""SELECT Tickers, Date, Close
                          FROM daily_stock_prices
                          WHERE Tickers = ? AND
                          Close = (SELECT MAX(Close)
                          FROM daily_stock_prices WHERE TICKERS = ?)""", conn, (ticker, ticker))
    return result
#calculate the percentage change between today's and yesterday's close
def calculate_daily_returns(df_daily: pd.DataFrame) -> pd.DataFrame:
    previous_close = df_daily.groupby("Tickers")["Close"].shift(1)
    df_daily["Daily Return %"] = (((df_daily["Close"] - previous_close) / previous_close * 100)).round(2)
    
    return df_daily

#biggest daily return
def get_biggest_daily_return(ticker: str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = db.run_query("""SELECT Tickers, Date, "Daily Return %" 
                          FROM daily_stock_prices
                          WHERE Tickers = ? AND "Daily Return %" 
                          = (SELECT MAX("Daily Return %")
                          FROM daily_stock_prices
                          WHERE Tickers = ?)""", conn, (ticker, ticker))
    return result
#worst daily return
def get_worst_daily_return(ticker: str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = db.run_query("""SELECT Tickers, Date, "Daily Return %"
                          FROM daily_stock_prices
                          WHERE Tickers = ? AND "Daily Return %"
                          = (SELECT MIN("Daily Return %")
                          FROM daily_stock_prices
                          WHERE Tickers = ?)
                          """, conn, (ticker, ticker))
    return result

#top 10 volume days
def top_ten_volume_days(ticker: str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = db.run_query("""SELECT Tickers, Date, Volume
                          FROM daily_stock_prices
                          WHERE Tickers = ? 
                          ORDER BY Volume DESC
                          LIMIT 10
                          """, conn, (ticker,))
    return result
    
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

#shows the progress of the closing price for each ticker together
def plot_all_closing_prices(df: pd.DataFrame, tickers: list):
    fig, ax = plt.subplots()
    for ticker in tickers:
        ticker_df = df[df["Tickers"] == ticker].copy()
        ticker_df["Date"] = pd.to_datetime(ticker_df["Date"])
        ticker_df = ticker_df.sort_values("Date")
        ticker_df.plot(x="Date",
                       y="Close",
                       ax=ax,
                       label=ticker
                       )
    plt.title(f"{[ticker for ticker in tickers]} closing prices over time") 
    plt.ylabel("Price ($)")
    plt.xlabel("Date")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    
#main method
def main():
    print("before connect")
    conn, cursor = db.connect_db()
    print("after connect")
    #create table in sqlite3
    db.create_table_daily(cursor,'daily_stock_prices')
    conn.commit()
    raw_data = download_stock_data(tickers)
    summary = calculate_summary(raw_data)
    #make dataframes
    df_summary = create_summary_dataframe(summary)
    df_daily = create_daily_dataframe(raw_data)
    calculate_daily_returns(df_daily)
    #write data to sql
    db.save_dataframe_summary(df_summary, 'stocks_summary',conn)
    db.save_dataframe_daily(df_daily,'daily_stock_prices', conn )
    with open("results.txt", 'w') as results:
        
        #Read Data from Sqlite
        for ticker in tickers:
            print(f"Report for {ticker}")
            highest_vol_day = get_highest_volume_day(ticker, conn)
            highest_close_day = get_highest_close_day(ticker, conn)
            biggest_daily_return = get_biggest_daily_return(ticker, conn)
            worst_daily_return = get_worst_daily_return(ticker, conn)
            top_ten_vol = top_ten_volume_days(ticker, conn)
            
            results.write(highest_vol_day.to_string(index=False))
            results.write(highest_close_day.to_string(index=False))
            results.write(biggest_daily_return.to_string(index=False))
            results.write(worst_daily_return.to_string(index=False))
            results.write(top_ten_vol.to_string(index=False))
            print(f"results written to {results.name}")
            #plot_closing_price(df_daily, ticker)
        plot_all_closing_prices(df_daily, tickers)
        #close connection
        conn.close()

if __name__ == "__main__":
    main()
