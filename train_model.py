import traceback
import numpy as np
import yfinance as yf
import pandas as pd
from textblob import TextBlob
from newsapi import NewsApiClient
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
from alpaca_trade_api.rest import REST
from config.settings import (
    ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, NEWSAPI_KEY
)
import matplotlib.pyplot as plt
import os

# Config
SYMBOL = 'AAPL'
WINDOW = 60
FUTURE_STEPS = 1
MODEL_PATH = 'outputs/latest_model.h5'
INITIAL_CAPITAL = 10000
EPOCHS = 50
BATCH_SIZE = 32

# Init APIs
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
newsapi = NewsApiClient(api_key=NEWSAPI_KEY) if NEWSAPI_KEY else None

def fetch_price_data(symbol):
    try:
        bars = list(api.get_bars(symbol, timeframe='1Day', limit=500))
        if len(bars) < 100:
            raise ValueError("Données Alpaca insuffisantes")
        closes = np.array([bar.c for bar in bars])
        timestamps = [bar.t.to_pydatetime() for bar in bars]
        return timestamps, closes
    except Exception:
        data = yf.download(symbol, period='2y', interval='1d', progress=False)
        closes = data['Close'].dropna().values
        timestamps = data.index.to_pydatetime()
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

def prepare_data(symbol, window=WINDOW):
    timestamps, closes = fetch_price_data(symbol)
    min_close, max_close = closes.min(), closes.max()
    norm_closes = (closes - min_close) / (max_close - min_close) if max_close != min_close else np.zeros_like(closes)

    print(f"Points récupérés : {len(closes)}")

    sentiments = np.array([get_sentiment_score(ts, symbol) for ts in timestamps])
    sentiments = sentiments.reshape(-1,1)

    features = np.hstack((norm_closes.reshape(-1,1), sentiments))

    X, y = [], []
    for i in range(len(features) - window):
        X.append(features[i:i+window])
        y.append(norm_closes[i+window])
    X, y = np.array(X), np.array(y)

    target_dates = timestamps[window:]

    print(f"Forme X={X.shape}, y={y.shape}")

    return X, y, target_dates, min_close, max_close, closes

def build_lstm_model(input_shape):
    model = Sequential([
        LSTM(50, activation='relu', input_shape=input_shape),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def main():
    try:
        print("Préparation des données...")
        X, y, target_dates, min_close, max_close, closes = prepare_data(SYMBOL)

        if len(X) == 0:
            print("Pas assez de données pour entraîner.")
            return

        model = build_lstm_model((X.shape[1], X.shape[2]))

        print("Entraînement du modèle...")
        early_stop = EarlyStopping(monitor='loss', patience=5, restore_best_weights=True)
        model.fit(X, y, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=2, callbacks=[early_stop])

        y_pred_norm = model.predict(X).flatten()

        y_pred = y_pred_norm * (max_close - min_close) + min_close
        y_true = y * (max_close - min_close) + min_close

        last_window = X[-1]
        next_pred_norm = model.predict(np.expand_dims(last_window, axis=0))[0][0]
        next_pred = next_pred_norm * (max_close - min_close) + min_close
        next_date = target_dates[-1] + pd.Timedelta(days=1)

        y_pred = np.append(y_pred, next_pred)
        pred_dates = np.append(target_dates, next_date)

        plt.figure(figsize=(15,7))
        plt.plot(target_dates, y_true, label='Prix Réel')
        plt.plot(pred_dates, y_pred, label='Prix Prédit', linestyle='--')
        plt.title(f"Évolution prix réel vs prédit - {SYMBOL}")
        plt.xlabel("Date")
        plt.ylabel("Prix")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        if not os.path.exists('outputs'):
            os.makedirs('outputs')
        plt.savefig('outputs/graph_price_real_vs_pred.png')
        plt.show()

        capital_reel = [float(INITIAL_CAPITAL)]
        capital_pred = [float(INITIAL_CAPITAL)]

        for i in range(1, len(y_true)):
            ratio = float(y_true[i]) / float(y_true[i-1]) if y_true[i-1] != 0 else 1.0
            capital_reel.append(capital_reel[-1] * ratio)

        for i in range(1, len(y_pred)):
            ratio = float(y_pred[i]) / float(y_pred[i-1]) if y_pred[i-1] != 0 else 1.0
            capital_pred.append(capital_pred[-1] * ratio)

        capital_reel = np.array(capital_reel, dtype=float)
        capital_pred = np.array(capital_pred, dtype=float)

        capital_dates = list(pred_dates)

        # Correction des longueurs incohérentes
        if len(capital_reel) < len(capital_dates):
            capital_reel = np.append(capital_reel, capital_reel[-1])

        if len(capital_reel) != len(capital_dates) or len(capital_pred) != len(capital_dates):
            raise ValueError(f"Longueurs incohérentes après correction: dates={len(capital_dates)}, réel={len(capital_reel)}, prédit={len(capital_pred)}")

        plt.figure(figsize=(15,7))
        plt.plot(capital_dates, capital_reel, label='Somme Cumulée Réelle (€)')
        plt.plot(capital_dates, capital_pred, label='Somme Cumulée Prédite (€)', linestyle='--')
        plt.title(f"Évolution du capital à partir de {INITIAL_CAPITAL}€ - {SYMBOL}")
        plt.xlabel("Date")
        plt.ylabel("Capital (€)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('outputs/graph_capital_cumule.png')
        plt.show()

        print("Fin du processus, graphiques sauvegardés dans outputs/")

    except Exception as e:
        print(f"Erreur: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
