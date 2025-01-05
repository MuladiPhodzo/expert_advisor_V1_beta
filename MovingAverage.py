import pandas as pd
import matplotlib.pyplot as plt
import Advisor as adv
import MetaTrader5 as mt5


class MovingAverageCrossover:
    
    mt = adv.mt5
    def __init__(self, data, fast_period=50, slow_period=200):
        """
        Initialize the strategy with data and parameters.
        
        :param data: DataFrame containing historical data (must include 'Close').
        :param fast_period: Period for the fast-moving average.
        :param slow_period: Period for the slow-moving average.
        """
        self.data = data
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.results = None

    def get_rates_from(self, symbol, timeframe, start_time, count):
        rates = mt5.copy_rates_from(symbol, timeframe, start_time, count)
        if rates is None:
            print(f"Failed to retrieve {symbol} rates, error code:", mt5.last_error())
        return rates
    def calculate_moving_averages(self):
        """Calculate the fast and slow moving averages."""
        if 'close' not in self.data.columns:
            raise ValueError("'Close' column is missing in the data.")
        self.data['Fast_MA'] = self.data['close'].rolling(window=self.fast_period).mean()
        self.data['Slow_MA'] = self.data['close'].rolling(window=self.slow_period).mean()

    def generate_signals(self):
        """Generate buy and sell signals based on moving average crossover."""
        self.data['Signal'] = 0
        self.data.loc[self.data['Fast_MA'] > self.data['Slow_MA'], 'Signal'] = 1  # Buy
        self.data.loc[self.data['Fast_MA'] < self.data['Slow_MA'], 'Signal'] = -1  # Sell

    def backtest_strategy(self):
        """
        Backtest the strategy by calculating strategy returns.
        
        :return: DataFrame containing backtesting results.
        """
        self.data['Position'] = self.data['Signal'].shift(1)  # Avoid lookahead bias
        self.data['Market_Returns'] = self.data['close'].pct_change()
        self.data['Strategy_Returns'] = self.data['Market_Returns'] * self.data['Position']
        self.data['Cumulative_Market_Returns'] = (1 + self.data['Market_Returns']).cumprod()
        self.data['Cumulative_Strategy_Returns'] = (1 + self.data['Strategy_Returns']).cumprod()
        self.results = self.data
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
        
    def run_moving_average_strategy(self, symbol, timeframe, start_time, count, fast_period=50, slow_period=200):
        """
        Fetch rates data and apply the Moving Average Crossover strategy.

        :param symbol: The symbol to fetch data for (e.g., 'EURUSD').
        :param timeframe: Timeframe for the rates (e.g., mt5.TIMEFRAME_M1).
        :param start_time: Starting datetime for fetching rates.
        :param count: Number of bars to fetch.
        :param fast_period: Fast moving average period.
        :param slow_period: Slow moving average period.
        """
        # Fetch data
        rates = self.get_rates_from(symbol, timeframe, start_time, count)
        if rates is None:
            print(f"Failed to retrieve data for {symbol}.")
            return None

        # Convert rates to a DataFrame
        rates_frame = pd.DataFrame(rates)
        rates_frame['time'] = pd.to_datetime(rates_frame['time'], unit='s')
        rates_frame.set_index('time', inplace=True)

        # Apply the strategy
        strategy = MovingAverageCrossover(rates_frame, fast_period, slow_period)
        strategy.calculate_moving_averages()
        strategy.generate_signals()
        results = strategy.backtest_strategy()

        # Plot the results
        strategy.plot_performance()
        return results

"""
# Example Usage
if __name__ == "__main__":
    # Load data
    data = pd.read_csv('your_data.csv', parse_dates=['Date'])
    data.set_index('Date', inplace=True)

    # Initialize and run the strategy
    strategy = MovingAverageCrossover(data, fast_period=50, slow_period=200)
    strategy.calculate_moving_averages()
    strategy.generate_signals()
    results = strategy.backtest_strategy()
    
    # Plot the performance
    strategy.plot_performance()
"""	