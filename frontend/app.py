import streamlit as st
import requests
import pandas as pd
import altair as alt

# =====================
# 🔹 CONFIG FASTAPI
# =====================
API_LOGEMENTS_URL = "http://127.0.0.1:8000/logements"
API_PREDICTION_URL = "http://127.0.0.1:8000/predict_prix_m2"

# =====================
# 🎨 STREAMLIT CONFIG
# =====================
st.set_page_config(page_title="Student Housing Finder", layout="wide")

# =====================
# 🔹 FONCTION API (avec cache)
# =====================
@st.cache_data
def fetch_logements(params):
    try:
        r = requests.get(API_LOGEMENTS_URL, params=params, timeout=10)
        r.raise_for_status()
        return pd.DataFrame(r.json())
    except Exception:
        st.error("❌ Impossible de récupérer les données depuis l’API")
        st.stop()

# =====================
# 🎨 CSS STYLE
# =====================
st.markdown("""
<style>
body { background: #f2f2f2; }
.card { background: white; border-radius: 15px; padding: 15px; box-shadow: 0 6px 18px rgba(0,0,0,0.08); margin-bottom: 20px; }
.card:hover { transform: translateY(-2px); transition: 0.2s ease; }
.price { font-size: 20px; font-weight: 700; margin-bottom: 5px; }
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
# 🔹 SESSION STATE
# =====================
if "search_params" not in st.session_state:
    st.session_state.search_params = {}
if "predictions" not in st.session_state:
    st.session_state.predictions = {}

# =====================
# 🔹 FORMULAIRE
# =====================
def render_form():
    with st.form("search_form"):
        ville = st.selectbox("Ville", ["", "Paris", "Marseille", "Lyon", "Bordeaux", "Lille", "Toulouse"])
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
            st.session_state.predictions = {}
            return True
    return False

# =====================
# 🔹 DASHBOARD
# =====================
# Centrer le titre et le formulaire si aucune recherche
if not st.session_state.search_params:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("👋 Hello, student!")
        st.subheader("Find the best student housing for you")
        st.write("")
        render_form()
else:
    # Layout après soumission : formulaire à gauche, résultats à droite
    col_left, col_right = st.columns([1, 2])
    with col_left:
        render_form()
    with col_right:
        params = st.session_state.search_params
        df = fetch_logements(params)

        st.subheader(f"🏠 {len(df)} logements trouvés")
        if df.empty:
            st.warning("Aucun logement trouvé pour ces critères.")
        else:
            df = df.sort_values(by="prix")

            # Metrics
            total_logements = len(df)
            prix_moyen = round(df['prix'].mean(), 2)
            prix_m2_moyen = round(df['prix_m2'].mean(), 2)
            surface_moyenne = round(df['surface'].mean(), 2)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("🏘️ Total logements", total_logements)
            m2.metric("💰 Prix moyen (€)", prix_moyen)
            m3.metric("📏 Surface moyenne (m²)", surface_moyenne)
            m4.metric("💡 Prix moyen €/m²", prix_m2_moyen)

            # Graphique combiné
            st.markdown("### 📊 Répartition rapide")
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('type_bien:N', title="Type de bien"),
                y=alt.Y('count():Q', title="Nombre de logements"),
                color=alt.Color('ville:N', title="Ville"),
                tooltip=['ville', 'type_bien', 'count()']
            ).properties(
                width=600,
                height=300
            )
            st.altair_chart(chart, use_container_width=True)

            # Cards
            n_cols = 3
            cols = st.columns(n_cols)
            for i, row in df.iterrows():
                col = cols[i % n_cols]
                with col:
                    with st.container():
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

                        # Prediction
                        if st.button(f"💡 Estimer prix/m²", key=f"pred_{row['id']}"):
                            try:
                                r = requests.get(API_PREDICTION_URL, params={
                                    "surface": row["surface"],
                                    "type_bien": row["type_bien"],
                                    "ville": row["ville"]
                                }, timeout=5)
                                r.raise_for_status()
                                data = r.json()
                                st.session_state.predictions[row['id']] = data["prix_m2_pred"]
                            except Exception:
                                st.error("Erreur lors de la prédiction")

                        if row['id'] in st.session_state.predictions:
                            st.success(f"💡 Prix estimé : {st.session_state.predictions[row['id']]} €/m²")