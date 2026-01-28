import pandas as pd
from .database import get_connection

def normalize_type_bien(type_bien):
    if not type_bien:
        return None

    t = type_bien.strip().upper()

    if "STUDIO" in t:
        return "STUDIO"
    if "T1" in t:
        return "T1"
    if "T2" in t:
        return "T2"
    if "T3" in t:
        return "T3"

    return t

def get_logements(ville=None, surface_min=None, type_bien=None):
    conn = get_connection()
    c = conn.cursor()
    query = "SELECT * FROM logements WHERE 1=1"
    params = []

    if ville:
        query += " AND ville LIKE ?"
        params.append(f"%{ville}%")
    if surface_min:
        query += " AND surface >= ?"
        params.append(surface_min)
    if type_bien:
        query += " AND type_bien = ?"
        params.append(normalize_type_bien(type_bien))

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=[
        "id", "titre", "prix", "surface", "prix_m2",
        "type_bien", "ville", "site_source", "image", "url", "date_scraping"
    ])
    
    # ❌ Supprimer les anomalies
    df = df[(df['prix'] > 100) & (df['surface'] > 10) & (df['prix_m2'] > 5)]

    # 🔼 Trier par prix/m² croissant
    df = df.sort_values(by="prix_m2", ascending=True).reset_index(drop=True)
    
    return df

