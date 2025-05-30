def place_order(api, symbol, side, qty=1):
    """
    Place un ordre via Alpaca.
    side: 'buy' ou 'sell'
    qty: quantité d'actions
    """
    try:
        api.submit_order(symbol=symbol, qty=qty, side=side, type='market', time_in_force='gtc')
        print(f"✅ Ordre {side} placé pour {qty} {symbol}")
    except Exception as e:
        print(f"❌ Erreur lors du passage d'ordre {side} pour {symbol}: {e}")
