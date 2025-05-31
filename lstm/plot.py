# lstm/plot.py (anciennement plot_predictions)
# =====================
import matplotlib.pyplot as plt

def plot_predictions(actual, predicted):
    plt.figure(figsize=(10,6))
    plt.plot(actual, color='black', label='Réel')
    plt.plot(predicted, color='green', label='Prédit')
    plt.title('Prédiction LSTM vs Réalité')
    plt.legend()
    plt.savefig("outputs/plots/lstm_prediction.png")
    plt.close()
