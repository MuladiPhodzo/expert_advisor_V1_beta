CREATE DATABASE trading_data;

USE trading_data;

CREATE TABLE candle_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10),
    timestamp DATETIME,
    open_price FLOAT,
    high_price FLOAT,
    low_price FLOAT,
    close_price FLOAT,
    volume FLOAT
);
