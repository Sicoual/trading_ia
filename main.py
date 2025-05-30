import datetime
import pandas as pd
from alpaca_trade_api.rest import REST
from config.settings import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL
from data.fetch_data import get_historical_data
from strategy.simple_moving_avg import generate_signals, print_latest_signals, plot_signals
from trade.trader import place_order
from news.fetch_news import fetch_news
from news.sentiment import analyze_sentiment

api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL)
GAFA_SYMBOLS = ['AAPL', 'GOOGL', 'AMZN', 'META']

def get_news_sentiment(symbol):
    today = datetime.datetime.utcnow().date()
    yesterday = today - datetime.timedelta(days=1)
    articles = fetch_news(symbol, from_date=str(yesterday), to_date=str(today), page_size=20)

    if not articles:
        return 0

    scores = []
    for article in articles:
        text = f"{article.get('title', '')} {article.get('description', '')}"
        score = analyze_sentiment(text)
        scores.append(score)

    return sum(scores) / len(scores) if scores else 0

def analyze_stock(symbol):
    print(f"\n📈 Analyse de {symbol}")

    today = datetime.datetime.utcnow().date()
    start_date = today - datetime.timedelta(days=100)
    end_date = today + datetime.timedelta(days=1)

    data = get_historical_data(symbol, start=start_date.isoformat(), end=end_date.isoformat())

    if data is None or data.empty:
        print(f"❌ Données indisponibles pour {symbol}")
        return

    signals = generate_signals(data)
    print_latest_signals(data, signals)
    plot_signals(data, symbol)

    # Affichage des positions J-1 et J-2
    if 'position' in signals.columns and len(signals) > 2:
        print(f"\n📍 Position à J-1 : {signals['position'].iloc[-2]}")
        print(f"📍 Position à J-2 : {signals['position'].iloc[-3]}")
    else:
        print("⚠️ Impossible de récupérer les positions à J-1 ou J-2.")

    # Sentiment des news
    sentiment = get_news_sentiment(symbol)
    print(f"\n📰 Sentiment moyen des news pour {symbol} : {sentiment:.2f}")

    # Prix de clôture
    def safe_scalar(val):
        return val.item() if hasattr(val, "item") else val

    close_j = safe_scalar(data['close'].iloc[-1])
    close_j1 = safe_scalar(data['close'].iloc[-2]) if len(data) > 1 else None
    close_j2 = safe_scalar(data['close'].iloc[-3]) if len(data) > 2 else None

    if close_j1 is not None and not pd.isna(close_j1):
        print(f"\n🕒 Prix J-1 : {close_j1:.2f}")
    else:
        print("Prix J-1 indisponible")

    if close_j2 is not None and not pd.isna(close_j2):
        print(f"🕒 Prix J-2 : {close_j2:.2f}")
    else:
        print("Prix J-2 indisponible")

    print(f"📅 Prix J   : {close_j:.2f}")

    # Logique de trading : Moyenne mobile + Sentiment + RSI
    last_position = signals['position'].iloc[-1]
    last_rsi = signals['rsi'].iloc[-1] if 'rsi' in signals.columns else None

    if last_position == 1 and sentiment > 0.2 and last_rsi is not None and last_rsi < 70:
        print("✅ Signal d'achat confirmé (MA + RSI < 70 + sentiment positif)")
        place_order(api, symbol, 'buy')
    elif last_position == -1 and sentiment < -0.2 and last_rsi is not None and last_rsi > 30:
        print("🔻 Signal de vente confirmé (MA + RSI > 30 + sentiment négatif)")
        place_order(api, symbol, 'sell')
    else:
        print("⚖️ Aucun signal clair ou conditions non remplies.")

def main():
    for symb in GAFA_SYMBOLS:
        analyze_stock(symb)

if __name__ == "__main__":
    main()
