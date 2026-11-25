CREATE TABLE public.daily_stock_prices (
    tickers character varying(10) NOT NULL,
    date date NOT NULL,
    close double precision,
    volume bigint,
    open double precision,
    high double precision,
    low double precision,
    dividends double precision,
    stock_splits double precision
);
ALTER TABLE ONLY public.daily_stock_prices
    ADD CONSTRAINT daily_stock_prices_pkey PRIMARY KEY (tickers, date);

CREATE VIEW public.daily_stock_prices_with_returns AS
WITH prices AS (
    SELECT
        tickers,
        date,
        open,
        high,
        low,
        close,
        volume,
        dividends,
        stock_splits,
        LAG(close) OVER (
            PARTITION BY tickers
            ORDER BY date
        ) AS previous_close
    FROM public.daily_stock_prices
    )
    SELECT tickers, date, open, high, low, close, volume, dividends, stock_splits,
    (close - previous_close) / NULLIF(previous_close, 0) * 100 AS daily_return_pct
    FROM prices;