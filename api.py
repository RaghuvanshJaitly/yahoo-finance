from fastapi import FastAPI, HTTPException
import queries
import database as db
from typing import Annotated
from fastapi import Query
from pydantic import BaseModel

class VolumeResponse(BaseModel):
    Tickers : str
    Date : str
    Volume : int

app = FastAPI()
avail = ['AAPL', 'GOOGL', 'AMZN', 'TSLA', 'MSFT']

# Check that the API is running
@app.get("/health")
def app_details():
    print("request recieved")
    return {"name": "Yahoo Finance", "status": "ok"}

# Validate the ticker and return it in uppercase.
@app.get("/stocks/{ticker}")
def get_ticker(ticker: str):
    ticker = ticker.upper()
    if ticker not in avail:
        raise HTTPException(
            status_code=404,
            detail='Ticker Not Found'
        )
    return {"ticker": ticker}

# Return the highest-volume day(s) for a supported ticker.
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

# Return up to 100 top-volume days, validating the input limit and response structure.       
@app.get("/stocks/{ticker}/top-volume", response_model=list[VolumeResponse])
def get_top_vol(ticker: str, limit: Annotated[int, Query(ge=1, le=100)] = 5):
    ticker = ticker.upper()
    if ticker not in avail:
        raise HTTPException(
            status_code=404,
            detail="Ticker not Found"
        )
    conn, cursor = db.connect_db()
    try:
        result = queries.top_ten_volume_days(ticker, conn, limit)
        if result.empty:
            raise HTTPException(
                status_code=404,
                detail="Records not found"
            )
        return result.to_dict(orient="records")
    finally:
        conn.close()