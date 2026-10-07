from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def app_details():
    print("request recieved")
    return {"name": "Yahoo Finance", "status": "ok"}

@app.get("/stocks/{ticker}")
def get_ticker(ticker: str):
    return {"ticker": ticker.upper()}