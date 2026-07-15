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
                          where Tickers = ? AND "Daily Return %" 
                          = (SELECT MAX("Daily Return %")
                          FROM daily_stock_prices
                          WHERE Tickers = ?)""", conn, (ticker, ticker))
    return result

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

    #Read Data from Sqlite
    #get the date with the highest volume for AAPL
    highest_vol_amzn = get_highest_volume_day("AMZN", conn)
    print('Highest Volume Day')
    print(highest_vol_amzn)
    highest_close_day = get_highest_close_day("AMZN", conn)
    print('Highest Closing Day')
    print(highest_close_day)
    biggest_gain_appl = get_biggest_daily_return("AAPL", conn)
    print('Biggest Daily return')
    print(biggest_gain_appl)
    #close connection
    conn.close()

if __name__ == "__main__":
    main()
