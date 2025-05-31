# === 1. fetch_lstm_data.py ===
import yfinance as yf
import pandas as pd

def get_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    data = data[['Close']]
    data.dropna(inplace=True)
    return data