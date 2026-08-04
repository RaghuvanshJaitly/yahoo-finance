print("starting main file")
import yfinance as yf
import pandas as pd
import sqlite3
import database as db
import matplotlib.pyplot as plt
import queries

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

#calculate the percentage change between today's and yesterday's close
def calculate_daily_returns(df_daily: pd.DataFrame) -> pd.DataFrame:
    previous_close = df_daily.groupby("Tickers")["Close"].shift(1)
    df_daily["Daily Return %"] = (((df_daily["Close"] - previous_close) / previous_close * 100)).round(2)
    
    return df_daily

#updates stock database with both summary and daily df
def update_stock_database(tickers, conn: sqlite3.Connection) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_data = download_stock_data(tickers)
    summary = calculate_summary(raw_data)
    df_summary = create_summary_dataframe(summary)
    df_daily = create_daily_dataframe(raw_data)
    df_daily = calculate_daily_returns(df_daily)
    db.save_dataframe_summary(df_summary, 'stocks_summary',conn)
    db.save_dataframe_daily(df_daily,'daily_stock_prices', conn )
    
    return df_summary, df_daily
    
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
    
#def needs_update_today(conn: sqlite3.Connection) -> bool:
    
#main method
def main():
    print("before connect")
    conn, cursor = db.connect_db()
    print("after connect")
    #create table in sqlite3
    db.create_table_daily(cursor,'daily_stock_prices')
    conn.commit()
    df_summary, df_daily = update_stock_database(tickers,conn)
    with open("results.txt", 'w') as results:
        
        #Read Data from Sqlite
        for ticker in tickers:
            highest_vol_day = queries.get_highest_volume_day(ticker, conn)
            highest_close_day = queries.get_highest_close_day(ticker, conn)
            biggest_daily_return = queries.get_biggest_daily_return(ticker, conn)
            worst_daily_return = queries.get_worst_daily_return(ticker, conn)
            top_ten_vol = queries.top_ten_volume_days(ticker, conn)
            positive_negative_counts = queries.positive_and_negative_count(ticker, conn)
            avg_monthly_close = queries.average_monthly_close(ticker, conn)
            days_above_avg_vol = queries.days_above_avg_vol(ticker, conn)

            results.write(f"\nReport for {ticker}\n")
            results.write(f"\nHighest Volume Day\n")
            results.write(highest_vol_day.to_string(index=False))
            results.write(f"\nHighest Close\n")
            results.write(highest_close_day.to_string(index=False))
            results.write(f"\nBiggest Daily Return\n")
            results.write(biggest_daily_return.to_string(index=False))
            results.write(f"\nWorst Daily Return\n")
            results.write(worst_daily_return.to_string(index=False))
            results.write(f"\nTop Ten Volume Days\n")
            results.write(f"{top_ten_vol.to_string(index=False)}\n")
            results.write(f"\nPositive and Negative Daily Return Count\n")
            results.write(f"{positive_negative_counts.to_string(index=False)}\n")
            results.write(f"\nAverage Monthly Close\n")
            results.write(f"{avg_monthly_close.to_string(index=False)}\n")
            results.write(f"\nDays Above Average Volume\n")
            results.write(f"{days_above_avg_vol.to_string(index=False)}\n")
            
            

        print(f"results written to {results.name}")
    #plot_closing_price(df_daily, ticker)
    plot_all_closing_prices(df_daily, tickers)
        #close connection
    conn.close()

if __name__ == "__main__":
    main()
