from fastapi import FastAPI, HTTPException
import queries
import database as db
from typing import Annotated
from fastapi import Query
from pydantic import BaseModel
from fastapi import Depends
import psycopg
from datetime import date

class VolumeResponse(BaseModel):
    tickers : str
    date : date
    volume : int

class HistoricalPriceResponse(BaseModel):

    tickers: str
    date: date
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    volume: int | None
    daily_return_pct: float | None
    
app = FastAPI()
avail = ['AAPL', 'GOOGL', 'AMZN', 'TSLA', 'MSFT']

def get_db():
    conn = db.connect_postgres()
    try:
        yield conn
    finally:
        conn.close()
        
# Check that the API is running
@app.get("/health")
def app_details():
    print("request recieved")
    return {"name": "Yahoo Finance", "status": "ok"}

#helper function
def validate_ticker(ticker: str) -> str:
    ticker = ticker.upper()
    if ticker not in avail:
        raise HTTPException(
            status_code=404,
            detail='Ticker not Found'
        )
    return ticker

# Validate the ticker and return it in uppercase.
@app.get("/stocks/{ticker}")
def get_ticker(valid_ticker: Annotated[str, Depends(validate_ticker)]):
    return {"ticker": valid_ticker}

# Return the highest-volume day(s) for a supported ticker.
@app.get("/stocks/{ticker}/highest-volume", response_model=list[VolumeResponse])
def get_highest_vol(valid_ticker: Annotated[str, Depends(validate_ticker)], conn: Annotated[psycopg.Connection, Depends(get_db)]):
    result = queries.get_highest_volume_day(valid_ticker, conn)
    if result.empty:
        raise HTTPException(
            status_code=404,
            detail='Records not found'
        )
    return result.to_dict(orient="records")


# Return up to 100 top-volume days, validating the input limit and response structure.       
@app.get("/stocks/{ticker}/top-volume", response_model=list[VolumeResponse])
def get_top_vol(valid_ticker: Annotated[str, Depends(validate_ticker)], conn: Annotated[psycopg.Connection, Depends(get_db)], limit: Annotated[int, Query(ge=1, le=100)] = 5):

    result = queries.top_ten_volume_days(valid_ticker, conn, limit)
    if result.empty:
        raise HTTPException(
            status_code=404,
            detail="Records not found"
        )
    return result.to_dict(orient="records")

# return historical price data
@app.get("/stocks/{ticker}/prices", response_model=list[HistoricalPriceResponse])
def get_historical_price(valid_ticker: Annotated[str, Depends(validate_ticker)], conn: Annotated[psycopg.Connection, Depends(get_db)], limit: Annotated[int, Query(ge=1, le=100)] = 30):
    
    result = queries.get_historical_prices(valid_ticker, conn, limit)
    if result.empty:
        raise HTTPException(
            status_code=404,
            detail="Records not found"
        )
    return result.to_dict(orient="records")