import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px

st.title("💸 Spese")

# User selector con radio button nella sidebar
st.sidebar.radio("", ('Nicola', 'Martina'), key='user')

# Connessione al DB
conn = sqlite3.connect("spese.db")
cursor = conn.cursor()
# Carica dati da DB in DataFrame
df = pd.read_sql_query("SELECT * FROM spese", conn)
df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
mesi_nomi = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
mesi_valori = list(range(1, 12))  # valori interni per filtro
anni = list(map(str, sorted(df['Data'].dt.year.dropna().unique(), reverse=True)))
#utenti = sorted(df['Da'].dropna().unique().tolist())
cursor.execute("SELECT nome FROM categorie ORDER BY id ASC")
categorie = [row[0] for row in cursor.fetchall()]
categorie_select = ["Tutte"] + categorie
# Mese e anno unici per selectbox
anno_corrente = str(datetime.today().year)
mese_corrente = datetime.today().month

st.write(st.session_state.user)

# Tabs
elenco, mensili, annuali, overall= st.tabs(["Elenco", "Statistiche Mensili", "Statistiche Annuali", "Statistiche Overall"])

with elenco:
    # Filtri
    # utente_sel = st.selectbox("Da", utenti)
    col1, col2 = st.columns(2)
    with col1:
        index_anno = anni.index(anno_corrente) if anno_corrente in anni else 0
        anno_sel = st.selectbox("Anno", anni, index = index_anno)
    with col2:
        mese_sel = st.selectbox("Mese", mesi_nomi, index = mese_corrente-1)
        mese_filtro = mesi_valori[mesi_nomi.index(mese_sel)]
    
    categoria_sel = st.selectbox("Categoria", categorie_select)

    df_filtrato = df.copy()

    df_filtrato['Categoria'] = df_filtrato['Categoria'].str.capitalize()

    if mese_filtro != "Tutti":
        df_filtrato = df_filtrato[df_filtrato['Data'].dt.month == mese_filtro]
    if anno_sel != "Tutti":
        df_filtrato = df_filtrato[df_filtrato['Data'].dt.year == int(anno_sel)]
    if categoria_sel != "Tutte":
        df_filtrato = df_filtrato[df_filtrato['Categoria'] == categoria_sel]
    # if utente_sel != "Tutti":
    #     mask_dividi = df_filtrato['Azione'].str.contains("Dividi", case=False, na=False)
    #     df_filtrato.loc[mask_dividi, 'Euro'] /= 2
    #     filtro = (df_filtrato['Da'] == utente_sel) | (
    #         (df_filtrato['Azione'] == 'Dividi') & (df_filtrato['Da'] != utente_sel)
    #     )
    #     df_filtrato = df_filtrato[filtro]
    mask_dividi = df_filtrato['Azione'].str.contains("Dividi", case=False, na=False)
    df_filtrato.loc[mask_dividi, 'Euro'] /= 2
    filtro = (df_filtrato['Da'] == st.session_state.user) | (
        (df_filtrato['Azione'] == 'Dividi') & (df_filtrato['Da'] != st.session_state.user)
    )
    df_filtrato = df_filtrato[filtro]

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
        col1, col2 = st.columns(2)
        with col1:
            index_anno = anni.index(anno_corrente) if anno_corrente in anni else 0
            anno_sel = st.selectbox("Anno", anni, index=index_anno, key="anno_mensile")
        with col2:
            mese_sel = st.selectbox("Mese", mesi_nomi, index=mese_corrente-1, key="mese_mensile")
            mese_filtro = mesi_valori[mesi_nomi.index(mese_sel)]

        # Carica tutte le categorie con id
        cursor.execute("SELECT id, nome FROM categorie ORDER BY id")
        categorie_df = pd.DataFrame(cursor.fetchall(), columns=["id", "Categoria"])
        categorie_df["Categoria"] = categorie_df["Categoria"].str.capitalize()

        # Filtro spese
        df_mensile = df.copy()
        df_mensile['Categoria'] = df_mensile['Categoria'].str.capitalize()
        df_mensile = df_mensile[df_mensile['Data'].dt.year == int(anno_sel)]
        df_mensile = df_mensile[df_mensile['Data'].dt.month == mese_filtro]
        df_mensile = df_mensile[(df_mensile['Da'] == st.session_state.user) | (
            (df_mensile['Azione'] == 'Dividi') & (df_mensile['Da'] != st.session_state.user)
        )]
        df_mensile.loc[df_mensile['Azione'].str.contains("Dividi", case=False, na=False), 'Euro'] /= 2

        # Totale per categoria
        spese_categoria = df_mensile.groupby("Categoria")["Euro"].sum().reset_index()
        spese_completo = categorie_df.merge(spese_categoria, on="Categoria", how="left")
        spese_completo["Euro"] = spese_completo["Euro"].fillna(0).round(2)

        # Colori per necessarie (id < 12) e voluttuarie (id >= 12)
        spese_completo["Colore"] = spese_completo["id"].apply(
            lambda x: "#8ecae6" if x < 12 else "#ffb703"
        )

        # Statistiche
        totale = spese_completo["Euro"].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Totale spese", f"€ {totale:,.2f}")

        # Grafico a barre orizzontali ordinato per id
        fig_bar = px.bar(
            spese_completo,
            y="Categoria",
            x="Euro",
            orientation="h",
            color="Colore",
            color_discrete_map="identity",
            text="Euro",
            title=f"Totale spese per categoria - {mese_sel} {anno_sel}",
        )

        fig_bar.update_traces(
            texttemplate="€ %{x:.2f}",  # formato etichette
            textposition="outside"
        )
        fig_bar.update_layout(
            yaxis=dict(title="", categoryorder="array", categoryarray=spese_completo["Categoria"][::-1]),
            xaxis=dict(visible=False),
            showlegend=False,
            margin=dict(t=40, l=0, r=80, b=0), 
            font=dict(size=14),
            height=50 * len(spese_completo) + 100
        )

        st.plotly_chart(fig_bar, use_container_width=True)



with annuali:
    #utente_sel = st.selectbox("Da", utenti, key="utente_annuale")
    index_anno = anni.index(anno_corrente) if anno_corrente in anni else 0
    anno_sel = st.selectbox("Anno", anni, index=index_anno, key="anno_annuale")
    # Implementa logica analoga per l'anno...

with overall:
    st.success("Olè")
    #utente_sel = st.selectbox("Da", utenti, key="utente_overall")
    # Implementa logica per tutte le spese...