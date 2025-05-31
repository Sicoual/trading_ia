# Variables
$pythonVersion = "3.10.11"
$installerUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe"
$installerPath = "$env:TEMP\python-$pythonVersion-amd64.exe"
$venvPath = ".\venv_tf310"

# Téléchargement de Python 3.10.11
Write-Output "Téléchargement de Python $pythonVersion..."
Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath

# Installation silencieuse de Python 3.10.11 (ajoute au PATH)
Write-Output "Installation de Python $pythonVersion..."
Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait

# Vérifie si python3.10 est accessible
Write-Output "Vérification de l'installation Python 3.10..."
$pythonExe = "python3.10"
$checkPython = & $pythonExe --version 2>&1

if ($checkPython -like "*Python 3.10*") {
    Write-Output "Python 3.10 installé avec succès: $checkPython"
} else {
    Write-Warning "Impossible de trouver python3.10 dans PATH. Veuillez vérifier l'installation."
    exit 1
}

# Création de l'environnement virtuel avec python3.10
Write-Output "Création de l'environnement virtuel dans $venvPath ..."
& $pythonExe -m venv $venvPath

# Activation de l'environnement virtuel
Write-Output "Activation de l'environnement virtuel..."
& "$venvPath\Scripts\Activate.ps1"

# Mise à jour de pip et installation de TensorFlow + packages nécessaires
Write-Output "Mise à jour de pip..."
pip install --upgrade pip

Write-Output "Installation des dépendances (tensorflow, numpy, pandas, etc.)..."
pip install tensorflow pandas numpy matplotlib scikit-learn textblob requests yfinance nltk newsapi-python tqdm

Write-Output "Installation terminée. Environnement virtuel prêt avec Python 3.10 et TensorFlow."

Write-Output "Pour activer l'environnement dans PowerShell à l'avenir, faites :"
Write-Output "    .\$venvPath\Scripts\Activate.ps1"

Write-Output "Vous pouvez maintenant lancer votre script python normalement."
