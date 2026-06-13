# train_ids.py
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

print("⏳ Étape 1 : Génération du dataset de trafic réseau universitaire (Simulation)...")

np.random.seed(42)
n_flux = 1000

# Génération des variables réseau classiques
duree_connexion = np.random.exponential(scale=1.5, size=n_flux) # en secondes
nombre_paquets = np.random.poisson(lam=15, size=n_flux)
octets_transferes = nombre_paquets * np.random.normal(500, 100, n_flux)

# Création du DataFrame
df = pd.DataFrame({
    'duree': np.clip(duree_connexion, 0.001, 60),
    'paquets': np.clip(nombre_paquets, 1, 5000),
    'octets': np.clip(octets_transferes, 64, 1000000)
})

# Initialisation des labels de trafic : 0=Normal, 1=DDoS, 2=PortScan, 3=ForceBrute
labels = []
for i, row in df.iterrows():
    # Logique de signature mathématique des menaces
    if row['paquets'] > 300 and row['octets'] > 500000:
        labels.append(1) # Attaque DDoS (Volume massif de paquets/octets)
    elif row['duree'] < 0.1 and row['paquets'] > 80:
        labels.append(2) # Scan de ports (Connexions ultra-rapides en chaîne)
    elif row['duree'] > 15 and row['paquets'] < 10:
        labels.append(3) # Tentative Force Brute (Connexions persistantes à faible volume)
    else:
        labels.append(0) # Trafic réseau Normal légitime

df['attaque_type'] = labels

# Séparation des données
X = df[['duree', 'paquets', 'octets']]
y = df['attaque_type']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("⚡ Étape 2 : Entraînement du classifieur multi-classes Random Forest...")
# Entraînement du modèle IDS
ids_model = RandomForestClassifier(n_estimators=100, random_state=42)
ids_model.fit(X_train, y_train)

# Évaluation du modèle
y_pred = ids_model.predict(X_test)
print("\n📊 Rapport de performance du Système de Détection d'Intrusions :")
target_names = ['Normal', 'DDoS', 'Port Scan', 'Force Brute']
print(classification_report(y_test, y_pred, target_names=target_names[:len(np.unique(y_test))]))

# Sauvegarde du modèle IDS
model_filename = 'unishield_ids_model.pkl'
joblib.dump(ids_model, model_filename)
print(f"\n✅ Succès ! Le modèle IDS a été sauvegardé sous : {model_filename}")