from tensorflow.keras.models import load_model
from data.fetch_data import get_stock_data
from data.preprocess_lstm import preprocess_data
from trade.alpaca_trader import init_alpaca, place_order
import datetime
import numpy as np

def predict_price(model_path, symbol, start, end, seq_len):
    model = load_model(model_path)
    data = get_stock_data(symbol, start, end)
    X, y, scaler = preprocess_data(data, seq_len)

    predicted_scaled = model.predict(X)
    predicted = scaler.inverse_transform(predicted_scaled)
    actual = scaler.inverse_transform(y.reshape(-1, 1))

    current_price = data['Close'].iloc[-1]
    predicted_price = predicted[-1][0]

    return predicted_price, current_price

def trade_based_on_prediction():
    SYMBOL = 'AAPL'
    START = '2023-01-01'
    END = datetime.date.today().isoformat()
    SEQ_LEN = 60
    MODEL_PATH = "outputs/lstm_model.h5"

    api = init_alpaca()
    predicted_price, current_price = predict_price(MODEL_PATH, SYMBOL, START, END, SEQ_LEN)
    place_order(api, SYMBOL, predicted_price, current_price)
