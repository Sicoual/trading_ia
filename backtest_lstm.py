import os
import traceback
import time
import numpy as np
import yfinance as yf
from textblob import TextBlob
from newsapi import NewsApiClient
from tensorflow.keras.models import load_model
from alpaca_trade_api.rest import REST
from config.settings import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, NEWSAPI_KEY
from trade.alpaca_trader import place_order

# Initialisation de l'API Alpaca
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)

SYMBOL = 'AAPL'
WINDOW = 60  # Nombre de minutes pour la fenêtre LSTM

def prepare_input_data_alpaca(api, symbol, window):
    bars = list(api.get_bars(symbol, timeframe='1Min', limit=window))
    if not bars or len(bars) < window:
        raise ValueError(f"Pas assez de données Alpaca pour {symbol}")
    closes = np.array([bar.c for bar in bars])
    min_close, max_close = closes.min(), closes.max()
    if max_close != min_close:
        norm_closes = (closes - min_close) / (max_close - min_close)
    else:
        norm_closes = np.zeros_like(closes)
    return norm_closes.reshape(1, window, 1), min_close, max_close

def prepare_input_data_yfinance(symbol, window, retries=3, delay=5):
    for attempt in range(retries):
        try:
            data = yf.download(symbol, period='1d', interval='1m', progress=False)
            closes = data['Close'].dropna().values
            if closes.size < window:
                raise ValueError(f"Pas assez de données yfinance (trouvé {closes.size})")
            closes = closes[-window:]
            min_close, max_close = closes.min(), closes.max()
            if max_close != min_close:
                norm_closes = (closes - min_close) / (max_close - min_close)
            else:
                norm_closes = np.zeros_like(closes)
            return norm_closes.reshape(1, window, 1), min_close, max_close
        except Exception as e:
            print(f"[yfinance] Erreur essai {attempt+1}: {e}")
            time.sleep(delay)
    raise RuntimeError("Échec récupération données via yfinance")

def prepare_input_data(api, symbol, window):
    try:
        return prepare_input_data_alpaca(api, symbol, window)
    except Exception as e:
        print(f"[Alpaca] Erreur : {e}. Tentative avec yfinance.")
        return prepare_input_data_yfinance(symbol, window)

def get_current_price(api, symbol):
    bars = list(api.get_bars(symbol, timeframe='1Min', limit=1))
    if bars:
        return bars[-1].c
    raise ValueError("Aucun prix actuel trouvé")

def get_news_sentiment(symbol):
    if not NEWSAPI_KEY:
        print("NEWSAPI_KEY non définie.")
        return 0.0

    newsapi = NewsApiClient(api_key=NEWSAPI_KEY)
    try:
        articles = newsapi.get_everything(q=symbol, language='en', sort_by='relevancy', page_size=50)
        sentiments = []
        for article in articles.get('articles', []):
            text = (article.get("title") or "") + ". " + (article.get("description") or "")
            if text.strip():
                blob = TextBlob(text)
                sentiments.append(blob.sentiment.polarity)
        return float(np.mean(sentiments)) if sentiments else 0.0
    except Exception as e:
        print(f"[NewsAPI] Erreur récupération news : {e}")
        return 0.0

def predict_price(model, input_data):
    predicted = model.predict(input_data, verbose=0)
    return predicted.flatten()[0]

def backtest_lstm_with_news():
    try:
        input_data, min_close, max_close = prepare_input_data(api, SYMBOL, WINDOW)
        model = load_model('outputs/lstm_model_compatible.h5')

        predicted_norm = predict_price(model, input_data)
        predicted_price = predicted_norm * (max_close - min_close) + min_close

        current_price = get_current_price(api, SYMBOL)

        news_sentiment = get_news_sentiment(SYMBOL)
        adjustment_factor = 1 + (news_sentiment * 0.02)  # Ajuste le poids du sentiment ici
        adjusted_price = predicted_price * adjustment_factor

        print(f"\n📈 Prix actuel : {current_price:.2f} USD")
        print(f"🔮 Prédiction LSTM (normalisée) : {predicted_norm:.5f}")
        print(f"🔮 Prédiction LSTM (réelle) : {predicted_price:.2f} USD")
        print(f"📰 Sentiment moyen : {news_sentiment:.3f}")
        print(f"⚖️ Prix ajusté (sentiment) : {adjusted_price:.2f} USD")

        if adjusted_price > current_price * 1.01:
            print("✅ Condition d'achat remplie → Placement de l’ordre")
            place_order(api, SYMBOL, 'buy', adjusted_price, current_price)
        else:
            print("❌ Condition non remplie → Aucun ordre passé")

    except Exception as e:
        print(f"[Erreur backtest] {e}")
        traceback.print_exc()

if __name__ == "__main__":
    backtest_lstm_with_news()
