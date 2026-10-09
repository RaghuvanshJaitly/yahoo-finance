from fastapi import FastAPI, HTTPException
import queries
import database as db
import sqlite3

app = FastAPI()
avail = ['AAPL', 'GOOGL', 'AMZN', 'TSLA', 'MSFT']

@app.get("/health")
def app_details():
    print("request recieved")
    return {"name": "Yahoo Finance", "status": "ok"}

@app.get("/stocks/{ticker}")
def get_ticker(ticker: str):
    ticker = ticker.upper()
    if ticker not in avail:
        raise HTTPException(
            status_code=404,
            detail='Ticker Not Found'
        )
    return {"ticker": ticker}

@app.get("/stocks/{ticker}/highest-volume")
def get_highest_vol(ticker: str):
    
    ticker = ticker.upper()
    if ticker not in avail:
            raise HTTPException(
            status_code=404,
            detail='Ticker Not Found'
        )
    conn, cursor = db.connect_db()
    try:
        result = queries.get_highest_volume_day(ticker, conn)
        if result.empty:
            raise HTTPException(
                status_code=404,
                detail='Records not found'
            )
        return result.to_dict(orient="records")
    finally:
        conn.close()
        
    