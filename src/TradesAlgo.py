import MetaTrader5 as mt5
import pandas as pd
import time

class MT5TradingAlgorithm:
    def __init__(self, data, symbol, lot_size=0.1, magic_number=1000, market_Bias=int):
        """
        Initialize the MT5 trading algorithm.
        :param symbol: The trading symbol (e.g., 'USDJPY').
        :param lot_size: The size of each trade.
        :param magic_number: Unique identifier for this strategy's trades.
        """
        self.data = data
        self.symbol = symbol
        self.lot_size = lot_size
        self.magic_number = magic_number
        self.current_position = None  # Track 'buy', 'sell', or None
        self.market_Bias = None

    def place_order(self, action):
        """
        Place a buy or sell order.
        :param action: 'buy' or 'sell'.
        """
        # Define order type
        order_type = mt5.ORDER_TYPE_BUY if action == 'buy' else mt5.ORDER_TYPE_SELL

        # Get symbol info
        symbol_info = mt5.symbol_info(self.symbol)
        if not symbol_info:
            print(f"Symbol {self.symbol} not found, cannot place order.")
            return False

        # Prepare order request
        price = mt5.symbol_info_tick(self.symbol).ask if action == 'buy' else mt5.symbol_info_tick(self.symbol).bid
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": self.lot_size,
            "type": order_type,
            "price": price,
            "deviation": 10,
            "magic": self.magic_number,
            "comment": f"{action.capitalize()} trade by strategy",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Send order
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order failed: {result.retcode}")
            return False

        print(f"{action.capitalize()} order placed at {price}.")
        self.current_position = action
        return True

    def execute_trades(self, data):
        """
        Execute trades based on signals in the data.
        :param data: Pandas DataFrame with a 'Signal' column.
        """
        for index, row in data.iterrows():
            signal = row['Signal']
            if signal == 1 and self.current_position != 'buy':
                self.place_order('buy')
            elif signal == -1 and self.current_position != 'sell':
                self.place_order('sell')
            time.sleep(1)  # Avoid API rate limits or overloading

    def close(self):
        """Shutdown MT5 connection."""
        mt5.shutdown()
        print("Disconnected from MetaTrader 5.")

# Example usage
'''if __name__ == "__main__":
    # Sample data (replace with your DataFrame)
    data = {
        'time': [
            "2024-11-18 03:15:00", "2024-11-18 03:30:00", "2024-11-18 03:45:00",
            "2024-11-18 04:00:00", "2024-11-18 04:15:00", "2024-11-28 10:00:00",
            "2024-11-28 10:15:00", "2024-11-28 10:30:00"
        ],
        'Signal': [-1, 1, 0, 1, -1, 1, 0, -1]
    }
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)

    # Initialize and execute trading algorithm
    mt5_algo = MT5TradingAlgorithm(symbol="USDJPY")
    try:
        mt5_algo.execute_trades(df)
    finally:
        mt5_algo.close()
'''
