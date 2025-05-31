import matplotlib.pyplot as plt

def plot_predictions(actual, predicted, symbol='Stock'):
    plt.figure(figsize=(14, 6))
    plt.plot(actual, label='Valeurs Réelles')
    plt.plot(predicted, label='Prédictions')
    plt.title(f'📈 Prédictions vs Réalité - {symbol}')
    plt.xlabel('Temps')
    plt.ylabel('Prix')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()