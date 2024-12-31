from os import path
import MetaTrader5_helper as mt5

def initialize(
    terminal_path: str = r"C:\Program Files\MetaTrader 5\terminal64.exe" # Correct path to the MetaTrader 5 terminal EXE file
) -> bool:
    """
    Initializes the MetaTrader 5 terminal.

    Parameters:
    terminal_path (str): Full path to the MetaTrader 5 terminal EXE file.

    Returns:
    bool: True if initialization is successful, False otherwise.
    """
    # Validate the path
    if not path.exists(terminal_path):
        raise FileNotFoundError(f"MetaTrader 5 terminal not found at {terminal_path}")
    
    # Initialize MetaTrader 5 with the path as a positional argument
    return mt5.initialize(terminal_path)
