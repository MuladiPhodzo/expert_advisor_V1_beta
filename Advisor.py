from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import MetaTrader5 as mt5
import MovingAverage as MA

register_matplotlib_converters()


class MetaTrader5Client:
    def __init__(self, symbols):
        self.symbols = symbols
        self.account_info = None
        self.terminal_info = None

    def initialize(self):
        if not mt5.initialize():
            print("initialize() failed, error code =", mt5.last_error())
            mt5.shutdown()
            return False
        self.account_info = mt5.account_info()
        self.terminal_info = mt5.terminal_info()
        return True

    def check_symbols_availability(self):
        available_symbols = [s.name for s in mt5.symbols_get()]
        for pair in self.symbols:
            if pair not in available_symbols:
                print(f"Pair {pair} is not available. Check if it's enabled in Market Watch.")
                return False
        return True

    def get_ticks_from(self, symbol, start_time, count):
        ticks = mt5.copy_ticks_from(symbol, start_time, count, mt5.COPY_TICKS_ALL)
        if ticks is None:
            print(f"Failed to retrieve {symbol} ticks, error code:", mt5.last_error())
        return ticks

    def get_ticks_range(self, symbol, start_time, end_time):
        ticks = mt5.copy_ticks_range(symbol, start_time, end_time, mt5.COPY_TICKS_ALL)
        if ticks is None:
            print(f"Failed to retrieve {symbol} ticks, error code:", mt5.last_error())
        return ticks

    def get_rates_from(self, symbol, timeframe, start_time, count):
        rates = mt5.copy_rates_from(symbol, timeframe, start_time, count)
        if rates is None:
            print(f"Failed to retrieve {symbol} rates, error code:", mt5.last_error())
       
        df = pd.DataFrame(rates)
        df.to_csv("rates_data.csv", index=False)
        return rates

    def get_rates_range(self, symbol, timeframe, start_time, end_time):
        rates = mt5.copy_rates_range(symbol, timeframe, start_time, end_time)
        if rates is None:
            print(f"Failed to retrieve {symbol} rates, error code:", mt5.last_error())
        
        df = pd.DataFrame(rates)
        df.to_csv("rates_data.csv", index=False)
        return rates

    def shutdown(self):
        mt5.shutdown()


class DataPlotter:
    @staticmethod
    def plot_ticks(ticks, title):
        if ticks is None or len(ticks) == 0:
            print("No data to plot.")
            return
        ticks_frame = pd.DataFrame(ticks)
        ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')
        plt.plot(ticks_frame['time'], ticks_frame['ask'], 'r-', label='ask')
        plt.plot(ticks_frame['time'], ticks_frame['bid'], 'b-', label='bid')
        plt.legend(loc='upper left')
        plt.title(title)
        plt.show()


if __name__ == "__main__":
    # Initialize client and symbols
    symbols = ["USDJPY", "USDCHF", "USDCAD", "USDZAR", "EURUSD"]
    client = MetaTrader5Client(symbols)
    rates_data = pd.read_csv("rates_data.csv")
    strategy = MA.MovingAverageCrossover(data= rates_data,fast_period=50, slow_period=200)

    if not client.initialize():
        exit()

    print("ACCOUNT.info: ", client.account_info)
    print("terminal.info: ", client.terminal_info)

    if not client.check_symbols_availability():
        client.shutdown()
        exit()

    # Fetch data
    usd_jpy_ticks = client.get_ticks_from("USDJPY", datetime(2024, 1, 28, 13), 1000)
    aud_usd_ticks = client.get_ticks_range("AUDUSD", datetime(2024, 1, 27, 13), datetime(2024, 1, 29, 13))
    eur_usd_rates = client.get_rates_from("EURUSD", mt5.TIMEFRAME_M15, datetime(2024, 11, 28, 13), 1000)
    usd_chf_rates = client.get_rates_from("USDCHF", mt5.TIMEFRAME_M1, datetime.now(), 1000)
    usd_cad_rates = client.get_rates_range("USDCAD", mt5.TIMEFRAME_M1, datetime(2024, 11, 27, 13), datetime(2024, 11, 28, 13))

    # Plot data
    print("Plotting USDJPY ticks...")
    DataPlotter.plot_ticks(usd_jpy_ticks, "USDJPY Ticks")
    for symbol in symbols:
        print(f"Plotting {symbol} rates...")
        rates = client.get_rates_from(symbol, mt5.TIMEFRAME_M1, datetime.now(), 1000)
        strategy.run_moving_average_strategy(symbol, mt5.TIMEFRAME_M15, datetime(2024, 11, 28, 13), 1000)
  
        if rates is not None:
            rates_frame = pd.DataFrame(rates)
            rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
            plt.plot(rates_frame['time'], rates_frame['close'], label='close')
            plt.title(f"{symbol} Rates")
            plt.legend()
            plt.show()
      # Shutdown client
    client.shutdown()
