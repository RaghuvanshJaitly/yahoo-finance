print("starting main file")
from finance_tracker import database as db
from finance_tracker import Application
from finance_tracker import data_pipeline as pipeline
from finance_tracker import queries
#main method
def main():
    tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
    print("before connect")
    with db.connect_postgres() as conn:
        print("after connect")
        pipeline.update_postgres_database(tickers,conn)
        df_analysis = queries.get_analysis_history(tickers, conn)
        app = Application.Application(tickers, conn, df_analysis)
        app.execute()
        
if __name__ == "__main__":
    main()
