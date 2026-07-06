import yfinance as yf
import pandas as pd
import sqlite3

#tickers
tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

#connect to database
def connect_db():
    try:
        conn = sqlite3.connect('stocks.db')
        return conn
    except Exception as e:
        print(f"An error occurred: {e}")

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

#save dataframe
def save_dataframe(dataframe: pd.DataFrame, table_name:str, conn:sqlite3.Connection):
    dataframe.to_sql(
    name=table_name,
    con=conn,
    if_exists='replace',
    index=False
    )
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

def run_query(query:str, conn: sqlite3.Connection, params) -> pd.DataFrame:
    result = pd.read_sql_query(query, conn, params=params)
    return result

#named report functions
def get_highest_volume_day(ticker: str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = run_query("SELECT Tickers, Date, Volume FROM daily_stock_prices WHERE Tickers = ? AND VOLUME = (SELECT MAX(Volume) FROM daily_stock_prices WHERE Tickers = ?)", conn, (ticker, ticker))
    return result

def get_highest_close_day(ticker:str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = run_query("SELECT Tickers, Date, Close FROM daily_stock_prices where Tickers = ? AND Close = (SELECT MAX(Close) FROM daily_stock_prices WHERE TICKERS = ?)", conn, (ticker, ticker))
    return result
#calculate the percentage change between today's and yesterday's close
def calculate_daily_returns(df_daily: pd.DataFrame) -> pd.DataFrame:
    previous_close = df_daily.groupby("Tickers")["Close"].shift(1)
    df_daily["Daily Return %"] = (((df_daily["Close"] - previous_close) / previous_close * 100)).round(2)
    
    return df_daily

#main method
def main():
    conn = connect_db()
    raw_data = download_stock_data(tickers)
    summary = calculate_summary(raw_data)
    #make dataframes
    df_summary = create_summary_dataframe(summary)
    df_daily = create_daily_dataframe(raw_data)
    calculate_daily_returns(df_daily)
    #write data to sql
    save_dataframe(df_summary, 'stocks_summary',conn)
    save_dataframe(df_daily,'daily_stock_prices', conn )

    #Read Data from Sqlite
    #get the date with the highest volume for AAPL
    highest_vol_amzn = get_highest_volume_day("AMZN", conn)
    print(highest_vol_amzn)
    highest_close_day = get_highest_close_day("AMZN", conn)
    print(highest_close_day)
    #close connection
    conn.close()

if __name__ == "__main__":
    main()
