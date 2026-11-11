print("starting main file")
import database as db
import Application
import data_pipeline as pipeline
#main method
def main():
    tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
    print("before connect")
    with db.connect_postgres() as conn:
        print("after connect")
        df_daily = pipeline.update_postgres_database(tickers,conn)
        app = Application.Application(tickers, conn, df_daily)
        app.execute()
        
if __name__ == "__main__":
    main()
