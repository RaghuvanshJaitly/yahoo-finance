import queries

class Application:
    
    def __init__(self, tickers, conn):
        self.tickers = tickers
        self.conn = conn
        self.menu = {
    1: "Highest Volume Day",
    2: "Highest Closing Day",
    3: "Biggest Daily Return",
    4: "Worst Daily Return",
    5: "Top 10 Volume Days",
    6: "Positive and Negative Daily Return % Count",
    7: "Average Monthly Close",
    8: "Number of Days Above Average Volume",
    9: "Compare Each Day's Closing Price with the Previous Day"}
        
        self.our_queries = {
    1: queries.get_highest_volume_day,
    2: queries.get_highest_close_day,
    3: queries.get_biggest_daily_return,
    4: queries.get_worst_daily_return,
    5: queries.top_ten_volume_days,
    6: queries.positive_and_negative_count,
    7: queries.average_monthly_close,
    8: queries.days_above_avg_vol,
    9: queries.previous_day_close}
    
    
    def help(self):
        print("""
Welcome to the Stock Analysis Application!

This application lets you explore and analyze historical stock market data using a collection of SQL-powered reports.

You can view price and volume statistics, daily returns, monthly trends, previous closing prices, and other useful insights for the available stock tickers.

Choose an option from the menu to get started.
""")
        print("0: exit")
        for command, option in self.menu.items():
            print(f"{command}: {option}")
            
    def query_handler(self, command: int):
        pass
            
        
    def execute(self):
        self.help()
        print()
        while True:
            try:
                command = int(input("Command: "))  
                
            except ValueError:
                print("Command should be a valid number from the menu")
                print("Restarting....")
                continue
            if command == 0:
                break
            if command not in self.menu:
                print("Command should be a valid number from the menu")
                print("Restarting....")
                continue
            else:
                ticker = input(f"Please Select Ticker from {', '.join(self.tickers)}: ")