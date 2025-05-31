import numpy as np
from sklearn.preprocessing import MinMaxScaler

def preprocess_data(df, seq_len=60):
    close_data = df[['Close']].values
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(close_data)

    X, y = [], []
    for i in range(seq_len, len(scaled_data)):
        X.append(scaled_data[i - seq_len:i])
        y.append(scaled_data[i])

    X, y = np.array(X), np.array(y)
    return X, y, scaler