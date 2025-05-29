import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px

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
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')

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

    df_filtrato['Categoria'] = df_filtrato['Categoria'].str.capitalize()

    if mese_filtro != "Tutti":
        df_filtrato = df_filtrato[df_filtrato['Data'].dt.month == mese_filtro]
    if anno_sel != "Tutti":
        df_filtrato = df_filtrato[df_filtrato['Data'].dt.year == int(anno_sel)]
    if categoria_sel != "Tutte":
        df_filtrato = df_filtrato[df_filtrato['Categoria'] == categoria_sel]
    if utente_sel != "Tutti":
        mask_dividi = df_filtrato['Azione'].str.contains("Dividi", case=False, na=False)
        df_filtrato.loc[mask_dividi, 'Euro'] /= 2
        # 3. Filtro: (Da == utente_sel) OR (Azione == 'Dividi' AND Da != utente_sel)
        filtro = (df_filtrato['Da'] == utente_sel) | (
            (df_filtrato['Azione'] == 'Dividi') & (df_filtrato['Da'] != utente_sel)
        )

        df_filtrato = df_filtrato[filtro]

    # Statistiche
    totale_euro = df_filtrato["Euro"].sum()

    # dati per grafico a torta
    spese_per_categoria = df_filtrato.groupby("Categoria")["Euro"].sum().reset_index()
    fig = px.pie(
        df_filtrato,
        values='Euro',
        names='Categoria',
        title="Spese per Categoria",
        hole=0.3,                    # effetto "donut" per eleganza
        color_discrete_sequence=px.colors.qualitative.Pastel,  # palette colori soft
    )

    fig.update_traces(
        textposition='inside',       # testi delle percentuali dentro le fette
        textinfo='percent+label',    # mostra percentuali + etichette
        marker=dict(line=dict(color='#000000', width=2)),
        domain=dict(x=[0, 1], y=[0.1, 1])
    )

    fig.update_layout(
        legend_title_text='Categorie',
        legend=dict(
            orientation="h",
            y=-0.1,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        margin=dict(t=40, b=0, l=0, r=0),  # margini stretti
        font=dict(size=14),
    )

    # Formattazione Euro e data
    df_filtrato["Euro"] = df_filtrato["Euro"].apply(lambda x: f"€ {x:,.2f}")
    df_filtrato['Data'] = df_filtrato['Data'].dt.strftime('%-d') + ' ' + df_filtrato['Data'].dt.month_name(locale='it_IT.utf8') + ' ' + df_filtrato['Data'].dt.strftime('%Y')

    # Totale spese
    st.write(f"**Totale spese:** € {totale_euro:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    # Tabella
    st.dataframe(df_filtrato, hide_index=True, use_container_width=True)
    # Grafico
    st.plotly_chart(fig, use_container_width=True)



    
