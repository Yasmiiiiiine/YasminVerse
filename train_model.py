# train_model.py
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

print("⏳ Étape 1 : Génération du dataset académique fictif...")

# Fixer la graine aléatoire pour avoir des résultats reproductibles
np.random.seed(42)
n_etudiants = 500

# Génération de variables explicatives réalistes
# Note interro : moyenne de 11/20, avec une variation
note_interro = np.clip(np.random.normal(11, 3.5, n_etudiants), 0, 20)

# Absences en TP/TD : la majorité a peu d'absences, quelques-uns en ont beaucoup
absences_tp = np.random.poisson(lam=1.8, size=n_etudiants)

# Heures de connexion à la plateforme : moyenne de 40h, liée inversement aux absences
heures_connexion = np.clip(np.random.normal(45, 15, n_etudiants) - (absences_tp * 4), 0, 120)

# Création du DataFrame Pandas
df = pd.DataFrame({
    'note_interro': note_interro,
    'absences_tp': absences_tp,
    'heures_connexion': heures_connexion
})

# Logique mathématique pour définir la cible 'echec' (0 = Réussite, 1 = Échec)
# Un étudiant a plus de chances d'échouer si sa note est basse et ses absences élevées
score_risque_theorique = (20 - df['note_interro']) * 0.4 + (df['absences_tp'] * 1.5) - (df['heures_connexion'] * 0.05)
seuil = np.percentile(score_risque_theorique, 75) # Environ 25% d'échecs
df['echec'] = (score_risque_theorique >= seuil).astype(int)

# Étape 2 : Séparation des données (X et y)
X = df[['note_interro', 'absences_tp', 'heures_connexion']]
y = df['echec']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("⚡ Étape 2 : Entraînement du modèle Random Forest...")
# Initialisation et entraînement du classifieur
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Étape 3 : Évaluation rapide
y_pred = model.predict(X_test)
print("\n📊 Rapport de performance du modèle :")
print(classification_report(y_test, y_pred))

# Étape 4 : Sauvegarde du modèle sur le disque
model_filename = 'edupredict_model.pkl'
joblib.dump(model, model_filename)
print(f"\n✅ Succès ! Le modèle a été entraîné et sauvegardé sous : {model_filename}")