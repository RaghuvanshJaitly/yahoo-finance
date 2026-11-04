import data_pipeline as pipeline
import pandas as pd

#test data integrity
def test_prepare_postgres_dataframe():
    df_daily = pd.DataFrame({
    "Tickers": ["AAPL"],
    "Date": ["2026-01-01"],
    "Open": [250.50],
    "High": [255.00],
    "Low": [248.20],
    "Close": [253.75],
    "Volume": [1500000],
    "Dividends": [0.0],
    "Stock Splits": [0.0],
    "Daily Return %": [1.25]})
    
    result = pipeline.prepare_postgres_dataframe(df_daily)
    
    assert result.columns.tolist() == [
    "tickers",
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "dividends",
    "stock_splits",
    "daily_return_pct"]   
    
    assert result.loc[result["tickers"] == "AAPL", "close"].iloc[0] == 253.75
    assert 'tickers' not in df_daily.columns
    assert 'Tickers' in df_daily.columns