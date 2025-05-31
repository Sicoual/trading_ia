import traceback
import time
import numpy as np
import yfinance as yf
import pandas as pd
from textblob import TextBlob
from newsapi import NewsApiClient
from tensorflow.keras.models import load_model
from alpaca_trade_api.rest import REST
from trade.alpaca_trader import place_order
from config.settings import (
    ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, NEWSAPI_KEY
)

# Config
SYMBOL = 'AAPL'
WINDOW = 60
MODEL_PATH = 'outputs/latest_model.h5'

# Init APIs
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
newsapi = NewsApiClient(api_key=NEWSAPI_KEY) if NEWSAPI_KEY else None

def load_keras_model_compatible(path):
    try:
        model = load_model(path)
        return model
    except Exception as e:
        print(f"Erreur lors du chargement du modèle: {e}")
        traceback.print_exc()
        return None

def fetch_price_data(symbol, window):
    """Récupère les données de prix via Alpaca, fallback yfinance"""
    try:
        bars = list(api.get_bars(symbol, timeframe='1Min', limit=window))
        if len(bars) < window:
            raise ValueError("Données Alpaca insuffisantes")
        closes = np.array([bar.c for bar in bars])
        timestamps = [bar.t.isoformat() for bar in bars]
        return timestamps, closes
    except Exception:
        # fallback yfinance
        data = yf.download(symbol, period='1d', interval='1m', progress=False)
        closes = data['Close'].dropna().values
        if len(closes) < window:
            raise RuntimeError("Pas assez de données yfinance")
        closes = closes[-window:]
        timestamps = data.index[-window:].to_pydatetime()
        timestamps = [ts.isoformat() for ts in timestamps]
        return timestamps, closes

def get_sentiment_score(timestamp, symbol=SYMBOL):
    if not newsapi:
        return 0.0
    date = pd.to_datetime(timestamp).strftime('%Y-%m-%d')
    try:
        articles = newsapi.get_everything(
            q=symbol, from_param=date, to=date, language='en',
            sort_by='relevancy', page_size=30
        )
        scores = []
        for article in articles['articles']:
            text = (article.get("title") or "") + ". " + (article.get("description") or "")
            score = TextBlob(text).sentiment.polarity
            scores.append(score)
        return np.mean(scores) if scores else 0.0
    except Exception:
        return 0.0

def prepare_input_data(symbol, window=WINDOW):
    timestamps, closes = fetch_price_data(symbol, window)
    min_close, max_close = closes.min(), closes.max()

    # Normalisation prix
    if max_close != min_close:
        norm_closes = (closes - min_close) / (max_close - min_close)
    else:
        norm_closes = np.zeros_like(closes)

    # Récupération sentiments
    sentiments = np.array([get_sentiment_score(ts, symbol) for ts in timestamps])

    # Construire features (prix normalisés + sentiment)
    features = np.stack((norm_closes, sentiments), axis=-1)

    return features.reshape(1, window, 2), min_close, max_close

def get_current_price(api, symbol):
    bars = list(api.get_bars(symbol, timeframe='1Min', limit=1))
    if bars:
        return bars[-1].c
    else:
        raise ValueError(f"Aucun prix disponible pour {symbol}")

def predict_price(model, input_data):
    predicted_norm = model.predict(input_data, verbose=0)
    return predicted_norm[0][0]

def main():
    try:
        print("📊 Préparation des données d'entrée...")
        input_data, min_close, max_close = prepare_input_data(SYMBOL)

        print("🔄 Chargement du modèle...")
        model = load_keras_model_compatible(MODEL_PATH)
        if model is None:
            print("❌ Impossible de charger le modèle, arrêt.")
            return

        predicted_norm_price = predict_price(model, input_data)
        predicted_price = predicted_norm_price * (max_close - min_close) + min_close

        current_price = get_current_price(api, SYMBOL)

        print(f"📈 Prix actuel: {current_price:.2f} USD")
        print(f"🔮 Prix prédit: {predicted_price:.2f} USD")

        # Condition d'achat : prix prédit > prix actuel + 1%
        if predicted_price > current_price * 1.01:
            print("✅ Condition d'achat remplie, passage de l'ordre d'achat...")
            place_order(api, SYMBOL, 'buy', predicted_price, current_price)
        else:
            print("⚠️ Condition non remplie, pas d'ordre passé.")

    except Exception as e:
        print(f"❌ Erreur dans le processus principal : {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
