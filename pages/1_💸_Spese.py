import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px

st.title("💸 Spese")

# Connessione al DB
conn = sqlite3.connect("spese.db")
cursor = conn.cursor()
# Carica dati da DB in DataFrame
df = pd.read_sql_query("SELECT * FROM spese", conn)
df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
mesi_nomi = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
mesi_valori = list(range(1, 13))  # valori interni per filtro
anni = list(map(str, sorted(df['Data'].dt.year.dropna().unique(), reverse=True)))
utenti = sorted(df['Da'].dropna().unique().tolist())
cursor.execute("SELECT nome FROM categorie ORDER BY id ASC")
categorie = ["Tutte"] + [row[0] for row in cursor.fetchall()]
# Mese e anno unici per selectbox
anno_corrente = str(datetime.today().year)
mese_corrente = datetime.today().month

# Tabs
elenco, mensili, annuali, overall= st.tabs(["Elenco", "Statistiche Mensili", "Statistiche Annuali", "Statistiche Overall"])

with elenco:
    # Filtri
    utente_sel = st.selectbox("Da", utenti)
    col1, col2 = st.columns(2)
    with col1:
        index_anno = anni.index(anno_corrente) if anno_corrente in anni else 0
        anno_sel = st.selectbox("Anno", anni, index = index_anno)
    with col2:
        mese_sel = st.selectbox("Mese", mesi_nomi, index = mese_corrente)
        mese_filtro = mesi_valori[mesi_nomi.index(mese_sel)]
    
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
        filtro = (df_filtrato['Da'] == utente_sel) | (
            (df_filtrato['Azione'] == 'Dividi') & (df_filtrato['Da'] != utente_sel)
        )
        df_filtrato = df_filtrato[filtro]

    # Statistiche
    totale_euro = df_filtrato["Euro"].sum()

    # dati per grafico a torta
    spese_per_categoria = df_filtrato.groupby("Categoria")["Euro"].sum().reset_index()
    fig = px.pie(df_filtrato, values='Euro', names='Categoria', title="Spese per Categoria", hole=0.3, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(textposition='inside', textinfo='percent+label', domain=dict(x=[0, 1], y=[0.1, 1]))
    fig.update_layout(
        legend_title_text='Categorie',
        legend=dict(orientation="h", y=-0.1, x=0.5, xanchor='center', yanchor='top'),
        margin=dict(t=40, b=0, l=0, r=0),  # margini stretti
        font=dict(size=14)
    )

    # Formattazione Euro e data
    df_filtrato["Euro"] = df_filtrato["Euro"].apply(lambda x: f"€ {x:,.2f}")
    df_filtrato['Data'] = df_filtrato['Data'].dt.strftime('%-d') + ' ' + df_filtrato['Data'].dt.month_name(locale='it_IT.utf8') + ' ' + df_filtrato['Data'].dt.strftime('%Y')

    # Totale spese
    st.metric("Totale spese", f"€ {totale_euro:,.2f}")
    # Tabella
    st.dataframe(df_filtrato, hide_index=True, use_container_width=True)
    # Grafico
    if not df_filtrato.empty:
        st.plotly_chart(fig, use_container_width=True)

with mensili:
    if df.empty:
        st.warning("La tabella 'spese' è vuota.")
    else:
        # Filtri
        utente_sel = st.selectbox("Da", utenti, key="utente_mensile")
        col1, col2 = st.columns(2)
        with col1:
            index_anno = anni.index(anno_corrente) if anno_corrente in anni else 0
            anno_sel = st.selectbox("Anno", anni, index=index_anno, key="anno_mensile")
        with col2:
            mese_sel = st.selectbox("Mese", mesi_nomi, index=mese_corrente, key="mese_mensile")
            mese_filtro = mesi_valori[mesi_nomi.index(mese_sel)]

with annuali:
    utente_sel = st.selectbox("Da", utenti, key="utente_annuale")
    index_anno = anni.index(anno_corrente) if anno_corrente in anni else 0
    anno_sel = st.selectbox("Anno", anni, index=index_anno, key="anno_annuale")
    # Implementa logica analoga per l'anno...

with overall:
    utente_sel = st.selectbox("Da", utenti, key="utente_overall")
    # Implementa logica per tutte le spese...


