import pandas as pd
import yfinance as yf
from alpaca_trade_api.rest import REST, TimeFrame
from config.settings import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL

api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)

def get_data_from_alpaca(symbol: str, start: str, end: str):
    try:
        df = api.get_bars(symbol, TimeFrame.Day, start=start, end=end).df
        df = df[df['symbol'] == symbol]
        df = df[['close']].copy()
        df.index = pd.to_datetime(df.index)
        return df
    except Exception as e:
        print(f"❌ Alpaca error for {symbol}: {e}")
        return None

def get_data_from_yfinance(symbol: str, start: str, end: str):
    try:
        df = yf.download(symbol, start=start, end=end)
        df = df[['Close']].rename(columns={'Close': 'close'})
        return df
    except Exception as e:
        print(f"❌ yFinance error for {symbol}: {e}")
        return None

def get_historical_data(symbol: str, start: str, end: str):
    print(f"📡 Téléchargement des données pour {symbol} de {start} à {end}...")
    
    data = get_data_from_alpaca(symbol, start, end)
    
    if data is None or data.empty:
        print("⚠️ Alpaca indisponible, tentative via yFinance...")
        data = get_data_from_yfinance(symbol, start, end)
    
    if data is None or data.empty:
        raise ValueError(f"❌ Impossible de récupérer les données pour {symbol}")
    
    return data
