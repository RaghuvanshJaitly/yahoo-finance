from fastapi.testclient import TestClient
from finance_tracker.api import app, get_db
import pytest
import psycopg
from dotenv import load_dotenv
import os

load_dotenv()


client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "name": "Yahoo Finance",
        "status": "ok"
    }

def test_lowercase_ticker():
    response = client.get("/stocks/aapl")
    assert response.status_code == 200
    assert response.json() == {
        "ticker": "AAPL"
    }

def test_invalid_ticker():
    response = client.get("/stocks/banana")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Ticker not Found"
    }

def test_query_top_volume_rejects_zero_limit():
    response = client.get("/stocks/googl/top-volume?limit=0")
    assert response.status_code == 422

@pytest.fixture(autouse=True)
def test_db():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        raise RuntimeError("TEST_DATABASE_URL is not configured")

    conn = psycopg.connect(url)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()[0]
            assert db_name == "stocks_test"
            
        def override_get_db():
            yield conn
        app.dependency_overrides[get_db] = override_get_db
        
        yield conn
    finally:
        app.dependency_overrides.pop(get_db, None)
        conn.rollback()
        conn.close()
    
@pytest.fixture
def sample_db(test_db):
        with test_db.cursor() as cursor:
            query = "INSERT INTO daily_stock_prices (tickers, date, volume) Values (%s, %s, %s)"
            query_data = [("AAPL", "2026-01-01", 100), ("AAPL", "2026-01-02", 900), ("AAPL", "2026-01-03", 400),("MSFT", "2026-01-01", 2000)]
            cursor.executemany(query, query_data)
            
def test_top_vol_return_correct_rows(sample_db):
    response = client.get("/stocks/aapl/top-volume?limit=2")
    assert response.status_code == 200
    assert response.json() == [
  {
    "tickers": "AAPL",
    "date": "2026-01-02",
    "volume": 900
  },
  {
    "tickers": "AAPL",
    "date": "2026-01-03",
    "volume": 400
  }]
    
def test_highest_volume_return_correct_row(sample_db):
    response = client.get("/stocks/aapl/highest-volume")
    assert response.status_code == 200
    assert response.json() == [
        {
    "tickers": "AAPL",
    "date": "2026-01-02",
    "volume": 900
  }
    ]

def test_highest_volume_no_record(sample_db):
    response = client.get("/stocks/googl/highest-volume")
    assert response.status_code == 404
    assert response.json() == {"detail": "Records not found"}
    
def test_historical_price_records(sample_db):
    response = client.get("/stocks/aapl/prices?limit=2")
    assert response.status_code == 200
    assert response.json() == [
  {
    "tickers": "AAPL",
    "date": "2026-01-03",
    "open": None,
    "high": None,
    "low": None,
    "close": None,
    "volume": 400,
    "daily_return_pct": None
  },
  {
    "tickers": "AAPL",
    "date": "2026-01-02",
    "open": None,
    "high": None,
    "low": None,
    "close": None,
    "volume": 900,
    "daily_return_pct": None
  }]

def test_historical_price_records_invalid_limit():
    response = client.get("/stocks/aapl/prices?limit=0")
    assert response.status_code == 422
    
def test_historical_prices_no_records():
    response = client.get("/stocks/googl/prices")
    assert response.status_code == 404
    assert response.json() == {"detail": "Records not found"}