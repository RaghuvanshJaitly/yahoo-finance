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

def run_query(query:str, conn: sqlite3.Connection) -> pd.DataFrame:
    result = pd.read_sql_query(query, conn)
    return result
#main method
def main():
    conn = connect_db()
    raw_data = download_stock_data(tickers)
    summary = calculate_summary(raw_data)
    #make dataframes
    df_summary = create_summary_dataframe(summary)
    df_daily = create_daily_dataframe(raw_data)

    #write data to sql
    save_dataframe(df_summary, 'stocks_summary',conn)
    save_dataframe(df_daily,'daily_stock_prices', conn )

    #Read Data from Sqlite
    #get the date with the highest volume for AAPL
    result = run_query("SELECT Date, Volume FROM daily_stock_prices WHERE Tickers = 'AAPL' AND VOLUME = (SELECT MAX(Volume) FROM daily_stock_prices WHERE Tickers = 'AAPL')", conn)
    print(result)
    #close connection
    conn.close()

if __name__ == "__main__":
    main()
