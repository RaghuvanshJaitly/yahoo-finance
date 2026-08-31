print("starting main file")
import database as db
import Application
import data_pipeline as pipeline

#main method
def main():
    tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
    print("before connect")
    conn, cursor = db.connect_db()
    print("after connect")
    #create table in sqlite3
    db.create_table_daily(cursor,'daily_stock_prices')
    conn.commit()
    df_summary, df_daily = pipeline.update_stock_database(tickers,conn)
    app = Application.Application(tickers, conn, df_daily)
    app.execute()
    #close connection
    print("closing connection")
    conn.close()

if __name__ == "__main__":
    main()
