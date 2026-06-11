import yfinance as yf

# defines the ticker symbol
ticker_symbol = "AAPL"

# create a ticker object 
ticker = yf.Ticker(ticker_symbol)

historical_data = ticker.history(period="1y") 
print(historical_data.columns)
