from finance_tracker import data_pipeline as pipeline
import pandas as pd
from datetime import date

#test data integrity
def test_prepare_postgres_dataframe():
    df_daily = pd.DataFrame({
    "Tickers": ["AAPL"],
    "Date": ["2026-01-01"],
    "Open": [float("nan")],
    "High": [255.00],
    "Low": [248.20],
    "Close": [253.75],
    "Volume": [1500000],
    "Dividends": [0.0],
    "Stock Splits": [0.0],})
    
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
    "stock_splits"]   
    
    assert result.loc[result["tickers"] == "AAPL", "close"].iloc[0] == 253.75
    assert 'tickers' not in df_daily.columns
    assert 'Tickers' in df_daily.columns
    assert isinstance(result['date'].iloc[0], date)
    assert result['date'].iloc[0] == date(2026, 1, 1)
    assert result["open"].iloc[0] is None