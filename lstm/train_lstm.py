# =====================
# lstm/train_lstm.py
# =====================
def train_lstm_model(model, X, y, epochs=10, batch_size=32):
    model.fit(X, y, epochs=epochs, batch_size=batch_size)
    model.save("outputs/lstm_model.keras")  # format moderne recommandé
    return model
