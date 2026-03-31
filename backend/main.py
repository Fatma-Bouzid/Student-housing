from fastapi import FastAPI
from typing import Optional
import pandas as pd
import joblib
import os
from backend.queries import get_logements
import numpy as np

# =====================
# 🔹 LOAD MODEL
# =====================
MODEL_PATH = "backend/ml_model.pkl"

if os.path.exists(MODEL_PATH):
    saved = joblib.load(MODEL_PATH)
    model = saved['model']
    preprocessor = saved['preprocessor']
    # features = saved['features']  # ❌ Supprimer cette ligne
    print("✅ Modèle ML chargé")
else:
    model = None
    preprocessor = None
    print("⚠️ Modèle ML non trouvé")
# =====================
# 🔹 FASTAPI INIT
# =====================
app = FastAPI(title="Student Housing API")

# =====================
# 🔹 ENDPOINT LOGEMENTS
# =====================
@app.get("/logements")
def logements(
    ville: Optional[str] = None,
    surface_min: Optional[float] = None,
    type_bien: Optional[str] = None,
    prix_max: Optional[int] = None
):
    df = get_logements(
        ville=ville,
        surface_min=surface_min,
        type_bien=type_bien,
        prix_max=prix_max
    )
    return df.to_dict(orient="records")

# =====================
# 🔹 ENDPOINT PREDICTION
# =====================
@app.get("/predict_prix_m2")
def predict_prix(surface: float, type_bien: str, ville: str):

    if model is None:
        return {"error": "Model not available"}

    # Création d'un DataFrame avec toutes les colonnes attendues
    data = pd.DataFrame({'surface': [surface], 'type_bien': [type_bien], 'ville': [ville]})

    # Préprocessing
    X_input = preprocessor.transform(data)

    # Prédiction (log -> prix/m2)
    pred_log = model.predict(X_input)[0]
    pred = np.exp(pred_log)

    return {"prix_m2_pred": round(pred, 2)}