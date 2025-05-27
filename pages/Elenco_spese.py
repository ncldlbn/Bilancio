import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Connessione al DB
conn = sqlite3.connect("spese.db")
cursor = conn.cursor()

st.title("Elenco Spese")

# Carica dati da DB in DataFrame
df = pd.read_sql_query("SELECT * FROM spese", conn)

if df.empty:
    st.warning("La tabella 'spese' è vuota.")
else:
    # Converti colonna data in datetime
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

    # Mese e anno unici per selectbox
    anno_corrente = str(datetime.today().year)
    mese_corrente = datetime.today().month

    # Indici predefiniti
    #index_anno = anni.index(anno_corrente) if anno_corrente in anni else 0
    #index_mese = mese_corrente  # mesi_nomi ha "Tutti" in posizione 0

    mesi_nomi = ["Tutti"] + ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
    mesi_valori = ["Tutti"] + list(range(1, 13))  # valori interni per filtro
    anni = ["Tutti"] + list(map(str, sorted(df['Data'].dt.year.dropna().unique(), reverse=True)))

    utenti = ["Tutti"] + sorted(df['Da'].dropna().unique().tolist())
    
    cursor.execute("SELECT nome FROM categorie ORDER BY id ASC")
    categorie = ["Tutte"] + [row[0] for row in cursor.fetchall()]

    # Filtri
    col1, col2 = st.columns(2)
    with col1:
        index_anno = anni.index(anno_corrente) if anno_corrente in anni else 0
        anno_sel = st.selectbox("Anno", anni, index = index_anno)
    with col2:
        mese_sel = st.selectbox("Mese", mesi_nomi, index = mese_corrente)
        mese_filtro = mesi_valori[mesi_nomi.index(mese_sel)]
    utente_sel = st.selectbox("Da", utenti)
    categoria_sel = st.selectbox("Categoria", categorie)

    df_filtrato = df.copy()

    if mese_filtro != "Tutti":
        df = df[df['Data'].dt.month == mese_filtro]
    if anno_sel != "Tutti":
        df = df[df['Data'].dt.year == int(anno_sel)]
    if utente_sel != "Tutti":
        df = df[df['Da'] == utente_sel]
    if categoria_sel != "Tutte":
        df = df[df['Categoria'] == categoria_sel]

    df["Euro"] = df["Euro"].apply(lambda x: f"€ {x:,.2f}")
    df['Data'] = df['Data'].dt.strftime('%-d') + ' ' + df['Data'].dt.month_name(locale='it_IT.utf8') + ' ' + df['Data'].dt.strftime('%Y')

    st.dataframe(df)
