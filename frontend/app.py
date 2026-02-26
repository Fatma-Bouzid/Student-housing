import streamlit as st
import requests
import pandas as pd

# =====================
# 🔹 FASTAPI CONFIG
# =====================
# 🔹 FASTAPI CONFIG
API_URL = "http://backend:8000/logements"


def fetch_logements(params):
    try:
        r = requests.get(API_URL, params=params, timeout=10)
        r.raise_for_status()
        return pd.DataFrame(r.json())
    except Exception as e:
        st.error("❌ Impossible de récupérer les données depuis l’API")
        st.stop()

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
a.button {
    display:inline-block;
    margin-top:8px;
    padding:6px 12px;
    border-radius:8px;
    background:#111;
    color:white !important;
    font-size:12px;
    font-weight:600;
    text-decoration:none;
}
</style>
""", unsafe_allow_html=True)

# =====================
# 🔹 NAVIGATION
# =====================
if "page" not in st.session_state:
    st.session_state.page = 1

# =====================
# 🔹 PAGE 1 : Recherche
# =====================
if st.session_state.page == 1:
    st.title("👋 Hello, student!")
    st.subheader("Find the best student housing for you")

    with st.form("search_form"):
        ville = st.selectbox(
            "Ville",
            ["", "Paris", "Marseille", "Lyon", "Bordeaux", "Lille", "Toulouse"]
        )
        type_bien = st.selectbox("Type de bien", ["", "STUDIO", "T1", "T2", "T3"])
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
        st.rerun()

# =====================
# 🔹 PAGE 2 : Résultats
# =====================
if st.session_state.page == 2:
    params = st.session_state.search_params
    df = fetch_logements(params)

    st.title("🏠 Best offers for you")
    st.caption(f"{len(df)} logements trouvés")

    if df.empty:
        st.warning("Aucun logement trouvé pour ces critères.")
    else:
        df = df.sort_values(by="prix")

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

    if st.button("🔙 Nouvelle recherche"):
        st.session_state.page = 1
        st.rerun()
