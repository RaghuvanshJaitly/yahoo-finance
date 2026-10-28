from fastapi.testclient import TestClient
from api import app
import pytest
import api
import pandas as pd
import sqlite3
import database as db

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

# Create a temporary database with known test data and make API connections use it.
# Monkeypatch restores the original connection function after the test.
@pytest.fixture
def sample_db(monkeypatch, tmp_path):
    sub_dir = tmp_path
    db_file = sub_dir / "temp_db.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    db.create_table_daily(cursor, "daily_stock_prices")
    query = "INSERT INTO daily_stock_prices (Tickers, Date, Volume) Values (?, ?, ?)"
    query_data = [("AAPL", "2026-01-01", 100), ("AAPL", "2026-01-02", 900), ("AAPL", "2026-01-03", 400),("MSFT", "2026-01-01", 2000)]
    
    cursor.executemany(query, query_data)
    conn.commit()
    conn.close()

    def replacement_function():
        test_conn = sqlite3.connect(db_file)
        test_cursor = test_conn.cursor()
        return test_conn, test_cursor
    monkeypatch.setattr(api.db, "connect_db", replacement_function)
    
def test_top_vol_return_correct_rows(sample_db):
    response = client.get("/stocks/aapl/top-volume?limit=2")
    assert response.status_code == 200
    assert response.json() == [
  {
    "Tickers": "AAPL",
    "Date": "2026-01-02",
    "Volume": 900
  },
  {
    "Tickers": "AAPL",
    "Date": "2026-01-03",
    "Volume": 400
  }]
    