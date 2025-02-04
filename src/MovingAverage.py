import pandas as pd
import matplotlib.pyplot as plt
import MetaTrader5 as mt5
import Advisor as adv
import os
import numpy as np
import TradesAlgo as Trades


class MovingAverageCrossover:

	def __init__(self,  symbol, data, fast_period=50, slow_period=200):
		"""
		Initialize the strategy with data and parameters.
		
		:param data: DataFrame containing historical data (must include 'close').
		:param fast_period: Period for the fast-moving average.
		:param slow_period: Period for the slow-moving average.
		"""
		self.data = data
		self.fast_period = fast_period
		self.slow_period = slow_period
		self.signals = None
		self.results = None
		self.symbol = symbol

	def get_rates_from(self, symbol, timeframe, start_time, count):
		
		"""Fetch historical rates from MetaTrader 5."""
		rates = mt5.copy_rates_from(symbol, timeframe, start_time, count)
		if rates is None:
				print(f"Failed to retrieve {symbol} rates, error code:", mt5.last_error())
		return rates

	def calculate_moving_averages(self):
		"""Calculate the fast and slow moving averages."""
		if 'close' not in self.data.columns:
				raise ValueError("'close' column is missing in the data.")
		self.data['Fast_MA'] = self.data['close'].rolling(window=self.fast_period).mean().shift()
		self.data['Slow_MA'] = self.data['close'].rolling(window=self.slow_period).mean().shift()
		print("Moving averages calculated.")

	def generate_signals(self):
		"""Generate buy and sell signals based on moving average crossover."""
		if 'Fast_MA' not in self.data.columns or 'Slow_MA' not in self.data.columns:
				raise ValueError("Moving averages are missing. Please run 'calculate_moving_averages()' first.")
		
		self.data['Signal'] = np.where(self.data['Fast_MA'] > self.data['Slow_MA'], 1, 0)
		self.data['Signal'] = np.where(self.data['Fast_MA'] < self.data['Slow_MA'], -1, 0)
	
		self.data['Crossover'] = self.data['Signal'].diff()
		# Remove unwanted columns
		self.data = self.data.drop(columns=['tick_volume', 'spread', 'real_volume'])

		# Remove rows with missing or empty values
		self.data = self.data.dropna()
		#print(self.data[['Signal', 'Crossover']].tail())
		print( self.data)
		print("Signals and crossovers generated.")
	
	def toCSVFile(self, rates):
			# Convert rates to DataFrame
			self.data = pd.DataFrame(rates)
			file_path = f'Logs\Rates\{self.symbol}_rates.csv'
			# Ensure the directory exists before writing
			os.makedirs(os.path.dirname(file_path), exist_ok=True)

			# Write DataFrame to CSV, creating the file if it doesn’t exist
			self.data.to_csv(file_path, index=True, mode='w', header=True)
	 
	def identify_entry_levels(self):
		"""Identify entry levels (buy and sell) based on crossovers."""
		if 'Crossover' not in self.data.columns:
				raise ValueError("Crossover data is missing. Please run 'generate_signals()' first.")

		data_with_time = self.data.reset_index()
		buy_signals = data_with_time[data_with_time['Signal'] == 1]
		sell_signals = data_with_time[data_with_time['Signal'] == -1]

		entry_levels = pd.concat([
				buy_signals[['time', 'close']].rename(columns={'close': 'Buy_Level'}),
				sell_signals[['time', 'close']].rename(columns={'close': 'Sell_Level'})
		], axis=1)

		self.signals = entry_levels.reset_index(drop=True)
		print("Entry levels identified.")

	def save_signals_to_csv(self, file_name="Logs/Signal_log.csv"):
		"""
		Save identified entry levels to a CSV file.
		- Creates the file if it doesn't exist.
		- Appends to the file if it already exists.
		"""
		if self.signals is not None:
			file_exists = os.path.isfile(file_name)
			if not file_exists:
				self.signals.to_csv(file_name, index=False, mode='w')
				print(f"New file created and entry levels saved to {file_name}.")
			else:
				self.signals.to_csv(file_name, index=False, mode='a', header=False)
				print(f"Entry levels appended to existing file {file_name}.")
		else:
				print("No signals to save. Please run 'identify_entry_levels()' first.")

	def backtest_strategy(self):
		"""Backtest the strategy by calculating strategy returns."""
		print("data", self.data)
		self.toCSVFile(self.data)
		self.data['Position'] = self.data['Signal'].shift(1)  # Avoid lookahead bias
		self.data['Market_Returns'] = self.data['close'].pct_change()
		self.data['Strategy_Returns'] = self.data['Market_Returns'] * self.data['Position']
		self.data['Cumulative_Market_Returns'] = (1 + self.data['Market_Returns']).cumprod()
		self.data['Cumulative_Strategy_Returns'] = (1 + self.data['Strategy_Returns']).cumprod()
		self.results = self.data.dropna().copy()  # Corrected version

		
		print("data after backtest", self.data)
		print("Backtest completed.")
		return self.results

	def plot_performance(self):
		"""Visualize the strategy performance against market performance."""
		if self.results is None:
				raise ValueError("No results available. Run backtest_strategy() first.")
		
		plt.figure(figsize=(12, 6))
		plt.plot(self.results.index, self.results['Cumulative_Market_Returns'], label='Market Returns', color='blue')
		plt.plot(self.results.index, self.results['Cumulative_Strategy_Returns'], label='Strategy Returns', color='green')
		plt.title('Moving Average Crossover Strategy Performance')
		plt.legend()
		plt.show()
			
	def plot_charts(self):
		if self.results is None:
				raise ValueError("Error: `self.results` is None. Run `backtest_strategy()` before plotting.")
		
		if 'Crossover' not in self.results.columns:
				raise ValueError("Error: 'Crossover' column is missing in `self.results`. Check data processing.")

		if 'close' not in self.data.columns or self.data['close'].empty:
				raise ValueError("No Close data available")

		plt.figure(figsize=(12, 6))

		# Plot the close price
		plt.plot(self.data.index, self.data['close'], label="Close", color='black')

		# Plot the fast and slow moving averages
		plt.plot(self.data.index, self.data['Fast_MA'], label=f"Fast MA ({self.fast_period})", color='blue')
		plt.plot(self.data.index, self.data['Slow_MA'], label=f"Slow MA ({self.slow_period})", color='red')

		# Plot buy signals (crossover == 2)
		plt.plot(self.results.loc[self.results['Crossover'] == 2].index, 
						self.results.loc[self.results['Crossover'] == 2, 'Fast_MA'], 
						'^', color='green', markersize=12, label="Buy Signal")

		# Plot sell signals (crossover == -2)
		plt.plot(self.results.loc[self.results['Crossover'] == -2].index, 
						self.results.loc[self.results['Crossover'] == -2, 'Fast_MA'], 
						'v', color='red', markersize=12, label="Sell Signal")

		# Add title and legend
		plt.title('Moving Average Crossover Signals')
		plt.legend(loc='upper left')
		plt.show()


			
	def run_moving_average_strategy(self, symbol, timeframe, start_time, count):
		"""
		Fetch rates data and apply the Moving Average Crossover strategy.

		:param symbol: The symbol to fetch data for (e.g., 'EURUSD').
		:param timeframe: Timeframe for the rates (e.g., mt5.TIMEFRAME_M15).
		:param start_time: Starting datetime for fetching rates.
		:param count: Number of bars to fetch.
		"""
		# Fetch data
		rates = self.data
		print(rates)
		
		if rates is None:
				print(f"Failed to retrieve data for {symbol}.")
				return None

		# Convert rates to a DataFrame
		rates_frame = pd.DataFrame(rates)
		rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
		rates_frame.set_index('time', inplace=True)

		# Apply the strategy
		strategy = MovingAverageCrossover( self.symbol ,rates_frame, self.fast_period, self.slow_period)
		strategy.calculate_moving_averages()
		strategy.generate_signals()
		strategy.identify_entry_levels()
		strategy.save_signals_to_csv()
		results = strategy.backtest_strategy()

		# Plot the results
		strategy.plot_charts()
		strategy.plot_performance()
		return results


"""# Example Usage
if __name__ == "__main__":
	# Assuming MetaTrader5 is initialized and connected
	from datetime import datetime

	strategy = MovingAverageCrossover(pd.DataFrame(), fast_period=50, slow_period=200)
	strategy.run_moving_average_strategy(
			symbol="EURUSD",
			timeframe=mt5.TIMEFRAME_M15,
			start_time=datetime(2024, 1, 1),
			count=1000
	)
"""