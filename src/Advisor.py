from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import MetaTrader5 as mt5
import MovingAverage as MA
import TradesAlgo as Algo
import os


register_matplotlib_converters()


class MetaTrader5Client:
	def __init__(self, symbols):
		self.symbols = symbols
		self.Ratesdata = None
		self.account_info = None
		self.terminal_info = None
		self.TF = None

	def initialize(self):
		if not mt5.initialize():
			print("initialize() failed, error code =", mt5.last_error())
			mt5.shutdown()
			return False
		'''self.account_info = mt5.account_info()
		self.terminal_info = mt5.terminal_info()'''
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

	def get_Price( symbol, price_type):
		info = mt5.symbol_info_tick(symbol)
		if price_type is None:
			print(f'"price_type" missing from {symbol} arguments', mt5.last_error())
   
		if price_type == "ask":
			return info.ask
		if price_type == "bid":
			return info.bid

	def get_rates_from(self, symbol, timeframe, start_time, count):
		rates = mt5.copy_rates_from(symbol, timeframe, start_time, count)
		if rates is None:
			print(f"Failed to retrieve {symbol} rates, error code:", mt5.last_error())

		return rates

	def get_rates_range(self, symbol, timeframe, start_time, end_time):
		rates = mt5.copy_rates_range(symbol, timeframe, start_time, end_time)
		if rates is None:
			print(f"Failed to retrieve {symbol} rates range, error code:", mt5.last_error())

		self.Ratesdata = pd.DataFrame(rates)
		return rates



	def toCSVFile(self, rates, file_path):
			# Convert rates to DataFrame
			self.Ratesdata = pd.DataFrame(rates)

			# Ensure the directory exists before writing
			os.makedirs(os.path.dirname(file_path), exist_ok=True)

			# Write DataFrame to CSV, creating the file if it doesn’t exist
			self.Ratesdata.to_csv(file_path, index=True, mode='w', header=True)



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

	@staticmethod
	def plot_rates(rates, title):
		if rates is None or len(rates) == 0:
			print("No data to plot.")
			return
		rates_frame = pd.DataFrame(rates)
		rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
		plt.plot(rates_frame['time'], rates_frame['close'], label='close')
		plt.title(title)
		plt.legend()
		plt.show()

if __name__ == "__main__":
	# Initialize client and symbols
	symbols = ["USDJPY", "USDCHF", "USDCAD", "USDZAR", "EURUSD"]
	client = MetaTrader5Client(symbols)
	client.TF = mt5.TIMEFRAME_H1

	if not client.initialize():
		exit()
	"""
	print("ACCOUNT.info: ", client.account_info)
	print("terminal.info: ", client.terminal_info)
 	"""

	if not client.check_symbols_availability():
		client.shutdown()
		exit()

	# Fetch data after every candle close
	# usd_jpy_ticks = client.get_ticks_from("USDJPY", datetime(2024, 1, 28, 13), 1000)
	# aud_usd_ticks = client.get_ticks_range("AUDUSD", datetime(2024, 1, 27, 13), datetime(2024, 1, 29, 13))
	# eur_usd_rates = client.get_rates_from("EURUSD", client.TF, datetime(2024, 11, 28, 13), 1000)
	# usd_chf_rates = client.get_rates_from("USDCHF", client.TF, datetime.now(), 1000)
	# usd_cad_rates = client.get_rates_range("USDCAD",client.TF, datetime(2024, 11, 27, 13), datetime(2024, 11, 28, 13))

	# if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
	# 	print("reading rates data from file............")
	# 	rates_data = pd.read_csv(file_path)
	# 	client.Ratesdata = rates_data
	# 	print(client.Ratesdata.head())
	# 	print(client.Ratesdata.columns)
	# else:
	# 	print(f"No such directory exists: '{file_path}'", FileNotFoundError)
  
	#fetch rates data and save to csv file
	# for symbol in symbols:
	# 	file_path = f"Logs\Rates\{symbol}rates_data.csv"
	# 	print(f"Fetching {symbol} rates...")
	# 	rangedRates = client.get_rates_range(symbol, client.TF, datetime(2024, 8, 1, 00), datetime.now())
		#rates = client.get_rates_from(symbol, client.TF, datetime.now(), 1000)
		#client.toCSVFile(rangedRates, file_path)
	# Plot data
	print("Assembling dataframes......")
	for symbol in symbols:
		print(f"Fetching {symbol} rates...")
		rangedRates = client.get_rates_range(symbol, client.TF, datetime(2024, 8, 1, 00), datetime.now())
		strategy = MA.MovingAverageCrossover(symbol, data=client.Ratesdata, fast_period=50, slow_period=200)
		print(client.Ratesdata)
		strategy.run_moving_average_strategy(symbol, mt5.TIMEFRAME_M15, datetime(2024, 11, 28, 13), 1000)


		# if rates is not None:
		# 	DataPlotter.plot_rates(rates, f"{symbol} Rates")
		# Shutdown client
	client.shutdown()
