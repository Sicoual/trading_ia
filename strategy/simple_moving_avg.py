import matplotlib.pyplot as plt
import os

def generate_signals(data, short_window=5, long_window=50, rsi_period=14):
    # Moyennes mobiles
    data['short_ma'] = data['close'].rolling(window=short_window).mean()
    data['long_ma'] = data['close'].rolling(window=long_window).mean()

    # RSI (Relative Strength Index)
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
    rs = gain / loss
    data['rsi'] = 100 - (100 / (1 + rs))

    # Signaux simples avec SMA crossover + RSI
    data['signal'] = 0
    buy_signal = (data['short_ma'] > data['long_ma']) & (data['rsi'] < 70)
    sell_signal = (data['short_ma'] < data['long_ma']) & (data['rsi'] > 30)
    data.loc[buy_signal, 'signal'] = 1
    data.loc[sell_signal, 'signal'] = -1

    # Remplir la position avec ffill
    data['position'] = data['signal'].ffill().fillna(0)

    return data


def print_latest_signals(data, signals):
    latest = signals.iloc[-1]
    print("\n📊 Dernières données et signaux :")
    print(latest[['close', 'short_ma', 'long_ma', 'rsi', 'signal', 'position']])

import matplotlib.pyplot as plt
import os

def plot_signals(data, symbol, show_seconds=5):
    plt.figure(figsize=(14, 7))
    plt.plot(data['close'], label='Prix', linewidth=1.5)
    plt.plot(data['short_ma'], label='Moyenne Mobile Courte', linestyle='--')
    plt.plot(data['long_ma'], label='Moyenne Mobile Longue', linestyle='--')

    buy_signals = data[data['signal'] == 1]
    sell_signals = data[data['signal'] == -1]

    plt.scatter(buy_signals.index, buy_signals['close'], label='Achat', marker='^', color='green')
    plt.scatter(sell_signals.index, sell_signals['close'], label='Vente', marker='v', color='red')

    plt.title(f'Signaux de trading pour {symbol}')
    plt.xlabel('Date')
    plt.ylabel('Prix')
    plt.legend()
    plt.grid(True)

    # Enregistrer la courbe
    save_dir = "outputs/plots"
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, f"{symbol}_signals.png")
    plt.savefig(file_path)

    print(f"🖼️ Courbe affichée temporairement et enregistrée ici : {file_path}")
    
    # Affichage temporaire
    plt.show(block=False)       # Affiche sans bloquer le programme
    plt.pause(show_seconds)     # Laisse affiché pendant x secondes
    plt.close()                 # Ferme la figure automatiquement


