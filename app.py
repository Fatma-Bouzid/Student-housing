import os
import sqlite3
import pandas as pd
import streamlit as st

# =====================
# 🔹 DATABASE
# =====================
DB_PATH = os.path.join(os.path.dirname(__file__), "data/logements.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def normalize_type_bien(type_bien):
    if not type_bien:
        return None
    t = type_bien.strip().upper()
    if "STUDIO" in t: return "STUDIO"
    if "T1" in t: return "T1"
    if "T2" in t: return "T2"
    if "T3" in t: return "T3"
    return t

def get_logements(ville=None, surface_min=None, type_bien=None, prix_max=None):
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
    if prix_max:
        query += " AND prix <= ?"
        params.append(prix_max)

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=[
        "id","titre","prix","surface","prix_m2",
        "type_bien","ville","site_source","image","url","date_scraping"
    ])
    df = df[(df['prix'] > 100) & (df['surface'] > 10) & (df['prix_m2'] > 5)]
    return df

# =====================
# 🎨 STREAMLIT CONFIG
# =====================
st.set_page_config(page_title="Student Housing Finder", layout="wide")

# =====================
# 🎨 CSS STYLE
# =====================
st.markdown("""
<style>
body { background: #f2f2f2; }
.card {
    background: white;
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}
.card:hover { transform: translateY(-2px); transition: 0.2s ease; }
.price { font-size: 24px; font-weight: 700; margin-bottom: 5px; }
.m2 { font-size: 13px; color: #666; margin-bottom: 5px; }
.city { font-size: 14px; font-weight: 600; }
.source { font-size: 11px; color: #999; margin-bottom: 5px; }
.badge { display:inline-block; padding:4px 10px; border-radius:999px; font-size:11px; font-weight:600; margin-bottom:5px; }
.badge.STUDIO { background:#fff1c1; }
.badge.T1 { background:#dbeafe; }
.badge.T2 { background:#dcfce7; }
.badge.T3 { background:#ede9fe; }
a.button { display:inline-block; margin-top:8px; padding:6px 12px; border-radius:8px; background:#111; color:white !important; font-size:12px; font-weight:600; text-decoration:none; }
</style>
""", unsafe_allow_html=True)

# =====================
# 🔹 PAGE 1 : Accueil
# =====================
if "page" not in st.session_state:
    st.session_state.page = 1

if st.session_state.page == 1:
    st.title("👋 Hello, student!")
    st.subheader("How can I help you? What's the housing you are looking for?")
    
    # Formulaire
    with st.form("search_form"):
        conn = get_connection()
        try:
            villes_dispo = pd.read_sql("SELECT DISTINCT ville FROM logements", conn)["ville"].tolist()
        except:
            villes_dispo = []
        conn.close()

        ville = st.selectbox("Ville", [""] + villes_dispo)
        type_bien = st.selectbox("Type de bien", ["", "STUDIO","T1","T2","T3"])
        surface_min = st.slider("Surface minimale (m²)", 0, 80, 0)
        prix_max = st.number_input("Budget maximum (€)", min_value=0, value=1000)
        
        submit = st.form_submit_button("🔎 Rechercher")

    if submit:
        st.session_state.search_params = {
            "ville": ville if ville else None,
            "type_bien": type_bien if type_bien else None,
            "surface_min": surface_min if surface_min > 0 else None,
            "prix_max": prix_max if prix_max > 0 else None
        }
        st.session_state.page = 2
        st.experimental_rerun()

# =====================
# 🔹 PAGE 2 : Résultats
# =====================
if st.session_state.page == 2:
    params = st.session_state.search_params
    df = get_logements(**params)
    df = df.sort_values(by="prix", ascending=True).reset_index(drop=True)

    st.title("🏠 Voici les logements les moins chers pour vous")
    st.caption(f"{len(df)} logements trouvés")

    if len(df) == 0:
        st.warning("Aucun logement trouvé pour ces critères.")
    else:
        cols = st.columns(3)
        for i, row in df.iterrows():
            col = cols[i % 3]
            with col:
                st.markdown(f"""
                <div class="card">
                    <span class="badge {row['type_bien']}">{row['type_bien']}</span>
                    <div class="price">{row['prix']} €</div>
                    <div class="m2">{row['surface']} m² • {row['prix_m2']} €/m²</div>
                    <div class="city">📍 {row['ville']}</div>
                    <div class="source">{row['site_source']}</div>
                    <a class="button" href="{row['url']}" target="_blank">Voir l'annonce</a>
                </div>
                """, unsafe_allow_html=True)

    if st.button("🔙 Rechercher autre chose"):
        st.session_state.page = 1
        st.experimental_rerun()
