import pandas as pd
import sqlite3
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor
import joblib

# =====================
# 🔹 LOAD DATA
# =====================
conn = sqlite3.connect("data/logements.db")
df = pd.read_sql("SELECT * FROM logements", conn)
conn.close()

# Nettoyage
df = df[(df['prix'] > 100) & (df['surface'] > 10) & (df['prix_m2'] > 5)]
df = df.dropna(subset=['surface', 'type_bien', 'ville'])

# Log transformation (IMPORTANT)
df['log_prix_m2'] = np.log(df['prix_m2'])

# Features
X = df[['surface', 'type_bien', 'ville']]
y = df['log_prix_m2']

# =====================
# 🔹 PREPROCESSING
# =====================
preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), ['type_bien', 'ville'])
], remainder="passthrough")

X_processed = preprocessor.fit_transform(X)

# =====================
# 🔹 TRAIN / TEST
# =====================
X_train, X_test, y_train, y_test = train_test_split(
    X_processed, y, test_size=0.2, random_state=42
)

# =====================
# 🔹 MODEL (RandomForest optimisé simple)
# =====================
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

model.fit(X_train, y_train)

# =====================
# 🔹 ÉVALUATION
# =====================
y_pred = np.exp(model.predict(X_test))
y_true = np.exp(y_test)

rmse = mean_squared_error(y_true, y_pred, squared=False)
mae = mean_absolute_error(y_true, y_pred)
r2 = r2_score(y_true, y_pred)

print(f"RandomForest → RMSE: {rmse:.2f}, MAE: {mae:.2f}, R2: {r2:.2f}")

# =====================
# 🔹 SAVE (TRÈS IMPORTANT)
# =====================
joblib.dump({
    "model": model,
    "preprocessor": preprocessor
}, "backend/ml_model.pkl")

print("✅ Modèle sauvegardé correctement")