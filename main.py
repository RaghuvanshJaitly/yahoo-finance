import yfinance as yf

data = {}
tickers = []

# defines the ticker symbol
ticker_symbol_apple = "AAPL"

# create a ticker object 
ticker = yf.Ticker(ticker_symbol_apple)

print("Apple")
# historical data
historical_data = ticker.history(period="1y")
info = []
info.append(historical_data) 


#basic financials
financials = ticker.financials
#print("\n Financials:")
#print(financials)

#fetch stock actions
stock_actions = ticker.actions
#print("\n stock actions")
#print(stock_actions)



ticker_symbol_mfst = "MSFT"
ticker_mfst = yf.Ticker(ticker_symbol_mfst)
tickers.append(ticker_symbol_apple)
tickers.append(ticker_symbol_mfst)
#print("Microsoft")
historical_data_mfst = ticker_mfst.history(period="1mo")
#print(historical_data_mfst)
for items in tickers:
    data[items] = historical_data[]
print(data)
