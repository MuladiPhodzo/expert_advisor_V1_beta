# the start up code goes here
from datetime import datetime
import matplotlib.pyplot as plt 
import pandas as pd 
from pandas.plotting import register_matplotlib_converters 
register_matplotlib_converters()
import MetaTrader5 as mt5


symbol = "USDJPY, USDCHF, USDCAD, USDJPY"
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    mt5.shutdown()
    exit()
 
# request connection status and parameters
print("terminal.info: ", mt5.terminal_info())
# get data on MetaTrader 5 version
print("version: ",mt5.version())

symbols = mt5.symbols_get()
print('Symbols: ', symbols)
available_symbols = [s.name for s in symbols]
if symbol not in available_symbols:
    print(f"Symbol {symbol} is not available. Check if it's enabled in Market Watch.")
    mt5.shutdown()
    exit()
# request 1000 ticks from EURAUD
euraud_ticks = mt5.copy_ticks_from("USDJPY", datetime(2020,1,28,13), 1000, mt5.COPY_TICKS_ALL)
if euraud_ticks is None:
    print("Failed to retrieve USDJPY ticks, error code:", mt5.last_error())
else:
    print('euraud_ticks(', len(euraud_ticks), ')')
    for val in euraud_ticks[:10]: print(val)
# request ticks from AUDUSD within 2019.04.01 13:00 - 2019.04.02 13:00
audusd_ticks = mt5.copy_ticks_range("AUDUSD", datetime(2024,1,27,13), datetime(2024,1,28,13), mt5.COPY_TICKS_ALL)
 
# get bars from different symbols in a number of ways
eurusd_rates = mt5.copy_rates_from("USDEUR", mt5.TIMEFRAME_M1, datetime(2020,1,28,13), 1000)
eurgbp_rates = mt5.copy_rates_from_pos("USDCHF", mt5.TIMEFRAME_M1, 0, 1000)
eurcad_rates = mt5.copy_rates_range("USDCAD", mt5.TIMEFRAME_M1, datetime(2020,1,27,13), datetime(2020,1,28,13))
print
# shut down connection to MetaTrader 5
mt5.shutdown()
 
#DATA
print('euraud_ticks(', len(euraud_ticks), ')')
for val in euraud_ticks[:10]: print(val)
 
print('audusd_ticks(', len(audusd_ticks), ')')
for val in audusd_ticks[:10]: print(val)
 
print('eurusd_rates(', len(eurusd_rates), ')')
for val in eurusd_rates[:10]: print(val)
 
print('eurgbp_rates(', len(eurgbp_rates), ')')
for val in eurgbp_rates[:10]: print(val)
 
print('eurcad_rates(', len(eurcad_rates), ')')
for val in eurcad_rates[:10]: print(val)
 
#PLOT
# create DataFrame out of the obtained data
ticks_frame = pd.DataFrame(euraud_ticks)
# convert time in seconds into the datetime format
ticks_frame['time']=pd.to_datetime(ticks_frame['time'], unit='s')
# display ticks on the chart
plt.plot(ticks_frame['time'], ticks_frame['ask'], 'r-', label='ask')
plt.plot(ticks_frame['time'], ticks_frame['bid'], 'b-', label='bid')
 
# display the legends
plt.legend(loc='upper left')
 
# add the header
plt.title('EURAUD ticks')
 
# display the chart
plt.show()
