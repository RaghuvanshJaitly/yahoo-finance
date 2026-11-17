CREATE TABLE public.daily_stock_prices (
    tickers character varying(10) NOT NULL,
    date date NOT NULL,
    close double precision,
    volume bigint,
    open double precision,
    high double precision,
    low double precision,
    dividends double precision,
    stock_splits double precision,
    daily_return_pct double precision
);
ALTER TABLE ONLY public.daily_stock_prices
    ADD CONSTRAINT daily_stock_prices_pkey PRIMARY KEY (tickers, date);