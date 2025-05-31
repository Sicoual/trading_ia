import alpaca_trade_api as tradeapi
from config.settings import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL

def init_alpaca(api_key, secret_key, base_url):
    return tradeapi.REST(api_key, secret_key, base_url, api_version='v2')

def place_order(api, symbol, side, current_price, predicted_price):
    predicted_price = float(predicted_price)  # Assure que c’est un float

    if side == 'buy':
        if predicted_price > current_price * 1.01:
            print(f"✅ Condition remplie : envoi d’un ordre d’achat pour {symbol}")
            # Exemple : passer un ordre d’achat d’une action
            api.submit_order(symbol=symbol, qty=1, side='buy', type='market', time_in_force='gtc')
        else:
            print("⚠️ Signal d'achat insuffisant, ordre non envoyé.")
    elif side == 'sell':
        if predicted_price < current_price * 0.99:
            print(f"✅ Condition remplie : envoi d’un ordre de vente pour {symbol}")
            api.submit_order(symbol=symbol, qty=1, side='sell', type='market', time_in_force='gtc')
        else:
            print("⚠️ Signal de vente insuffisant, ordre non envoyé.")
    else:
        print(f"❌ Action inconnue '{side}'")

