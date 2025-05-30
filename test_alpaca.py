import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = os.getenv("ALPACA_BASE_URL")

print(f"API_KEY={API_KEY}")
print(f"SECRET_KEY={SECRET_KEY}")
print(f"BASE_URL={BASE_URL}")

if not API_KEY or not SECRET_KEY or not BASE_URL:
    raise ValueError("Les clés API Alpaca ne sont pas correctement définies dans le fichier .env")

api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

account = api.get_account()
print("Compte Alpaca connecté:")
print(f"ID : {account.id}")
print(f"Statut : {account.status}")
print(f"Cash disponible : {account.cash}")
