# 🤖 Trading IA avec Alpaca

Ce projet vise à créer un **système de trading automatique intelligent** en utilisant l'API d'Alpaca pour récupérer les données financières et exécuter les ordres. Le système applique une stratégie de trading basée sur des indicateurs techniques (ex: moyennes mobiles) et peut être étendu avec des modèles de machine learning ou d'analyse de sentiment.

---

## 🗂️ Arborescence du projet
trading_ia/
│
├── .env # Clés API stockées ici
├── requirements.txt # Dépendances du projet
├── README.md # Présentation du projet
│
├── main.py # Script principal de trading
│
├── config/ # Paramètres de configuration
│ └── settings.py # Chargement des variables d’environnement
│
├── data/ # Téléchargement et gestion des données
│ └── fetch_data.py # Récupère les données boursières via Alpaca
│
├── strategy/ # Contient les stratégies de trading
│ └── simple_moving_avg.py # Exemple de stratégie basée sur les SMA
│
├── trade/ # Gestion des ordres et portefeuille
│ ├── trader.py # Envoie les ordres d’achat/vente
│ └── portfolio.py # Gère le portefeuille (à implémenter)
│
├── analysis/ # Analyse et backtests
│ └── backtest.py # Simulation de stratégie (à implémenter)
│
└── utils/ # Fonctions utilitaires
└── logger.py # Logging (info, erreur, etc.)

Installe les dépendances :

pip install -r requirements.txt
Crée un fichier .env :

env
Copier
Modifier
ALPACA_API_KEY=ta_clé_api
ALPACA_SECRET_KEY=ton_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets
NEWSAPI_KEY=clé_newsapi_si_utilisée

▶️ Lancement
Lance le fichier principal :
python main.py
Il exécutera une stratégie simple (ex: moyenne mobile) sur l’action AAPL.

📦 Modules principaux
Module	Description
fetch_data.py	Récupère les données historiques Alpaca
simple_moving_avg.py	Génère les signaux d’achat/vente
trader.py	Passe les ordres via l’API
main.py	Orchestration générale

🚀 À venir
Backtesting historique

Modèles IA de prédiction (ex: RandomForest, LSTM)

Analyse de sentiment via NewsAPI

Interface Web ou Dashboard
