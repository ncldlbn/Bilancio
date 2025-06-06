import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px

st.markdown("""
<style>
div.stButton > button {
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

st.title("💰 Entrate")

# User selector con radio button nella sidebar
# Inizializza una volta sola
if "user" not in st.session_state:
    st.session_state.user = "Nicola"
# Mostra il radio nella sidebar, con chiave SEPARATA
selezione = st.sidebar.radio(
    "Seleziona utente",
    options=["Nicola", "Martina"],
    index=["Nicola", "Martina"].index(st.session_state.user),
    key="user_radio"
)
# Aggiorna lo stato persistente solo se cambia
if selezione != st.session_state.user:
    st.session_state.user = selezione
    st.rerun()

# Connessione al DB
conn = sqlite3.connect("spese.db")
cursor = conn.cursor()
# Carica dati da DB in DataFrame
df = pd.read_sql_query("SELECT * FROM entrate", conn)
df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
mesi_nomi = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
mesi_valori = list(range(1, 12))  # valori interni per filtro
anni = list(map(str, sorted(df['Data'].dt.year.dropna().unique(), reverse=True)))
# Mese e anno unici per selectbox
anno_corrente = str(datetime.today().year)
mese_corrente = datetime.today().month


col1, col2 = st.columns(2)
with col1:
    index_anno = anni.index(anno_corrente) if anno_corrente in anni else 0
    anno_sel = st.selectbox("Anno", anni, index = index_anno)
with col2:
    mese_sel = st.selectbox("Mese", mesi_nomi, index = mese_corrente-1)
    mese_filtro = mesi_valori[mesi_nomi.index(mese_sel)]

if not df.empty:
    # Filtro
    df_filtrato = df.copy()

    # Filtro mese e anno
    if mese_filtro != "Tutti":
        df_filtrato = df_filtrato[df_filtrato['Data'].dt.month == mese_filtro]
    if anno_sel != "Tutti":
        df_filtrato = df_filtrato[df_filtrato['Data'].dt.year == int(anno_sel)]

    # Copia da mostrare, formattata
    df_mostra = df_filtrato.copy()
    df_mostra["Euro"] = df_mostra["Euro"].apply(lambda x: f"€ {x:,.2f}")
    df_mostra['Data'] = df_mostra['Data'].dt.strftime('%-d %B %Y')

    # Mostra tabella
    st.dataframe(df_mostra, hide_index=True, use_container_width=True)