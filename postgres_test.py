import database as db

conn = db.connect_postgres()
with conn:
    with conn.cursor() as cur:
        sql = "INSERT INTO daily_stock_prices(tickers, date, volume) VALUES (%s, %s, %s)"
        cur.execute(sql, ("TSLA", "2026-01-01", 1500000))
        sql2 = "INSERT INTO daily_stock_prices(tickers, date, volume) VALUES (%s, %s, %s)"
        cur.execute(sql2, ("TSLA", "2026-01-01", 15000200))
