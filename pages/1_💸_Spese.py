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

st.title("💸 Spese")




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
azioni_disponibili = ["", "Dividi", "Dai", "Saldo"]

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

    # Filtro
    df_filtrato = df.copy()
    df_filtrato['Categoria'] = df_filtrato['Categoria'].str.capitalize()

    # Filtro mese e anno
    if mese_filtro != "Tutti":
        df_filtrato = df_filtrato[df_filtrato['Data'].dt.month == mese_filtro]
    if anno_sel != "Tutti":
        df_filtrato = df_filtrato[df_filtrato['Data'].dt.year == int(anno_sel)]
    if categoria_sel != "Tutte":
        df_filtrato = df_filtrato[df_filtrato['Categoria'] == categoria_sel]

    # Logica divisione spesa
    mask_dividi = df_filtrato['Azione'].str.contains("Dividi", case=False, na=False)
    df_filtrato.loc[mask_dividi, 'Euro'] /= 2
    filtro = (df_filtrato['Da'] == st.session_state.user) | (
        (df_filtrato['Azione'] == 'Dividi') & (df_filtrato['Da'] != st.session_state.user)
    )
    df_filtrato = df_filtrato[filtro]

    # Copia da mostrare, formattata
    df_mostra = df_filtrato.copy()
    df_mostra["Euro"] = df_mostra["Euro"].apply(lambda x: f"€ {x:,.2f}")
    df_mostra['Data'] = df_mostra['Data'].dt.strftime('%-d %B %Y')

    # Mostra tabella
    st.dataframe(df_mostra, hide_index=True, use_container_width=True)

    # Interfaccia modifica/elimina
    if not df_filtrato.empty:
        with st.expander("✏️ Modifica o elimina spesa", expanded=False):
            record_id = st.selectbox("Seleziona un record da modificare/eliminare", df_filtrato['id'], key="modifica_id")
            record = df_filtrato[df_filtrato['id'] == record_id].iloc[0]

            # Input dinamici (nessun form)
            data = st.date_input("Data", pd.to_datetime(record["Data"]), key="data_input")
            euro = st.number_input("Euro", value=record["Euro"], step=0.01, key="euro_input")

            # Categoria: fix per maiuscola
            try:
                idx_cat = categorie.index(record["Categoria"].capitalize())
            except ValueError:
                idx_cat = 0
            categoria = st.selectbox("Categoria", categorie, index=idx_cat, key="categoria_input")

            descrizione = st.text_input("Descrizione", value=record["Descrizione"], key="descrizione_input")

            azione = st.selectbox("Azione", azioni_disponibili, 
                                index=azioni_disponibili.index(record["Azione"]) if record["Azione"] in azioni_disponibili else 0, 
                                key="azione_input")

            if azione == "Dividi":
                div_factor = st.number_input("Fattore di divisione", min_value=0.0, max_value=1.0, step=0.1,
                                            value=record.get("div_factor", 0.5), format="%.2f", key="div_factor_input")
            else:
                div_factor = None

            # Pulsanti
            col1, col2 = st.columns(2)
            if col1.button("💾 Salva modifiche"):
                cursor.execute("""
                    UPDATE spese SET 
                        Data = ?, Euro = ?, Categoria = ?, Descrizione = ?, 
                        Azione = ?, Da = ?, div_factor = ? 
                    WHERE id = ?
                """, (str(data.strftime('%d/%m/%Y')), euro, categoria, descrizione, azione, record["Da"], div_factor, record_id))
                conn.commit()
                st.success("Modifiche salvate.")
                st.rerun()

            if col2.button("🗑️ Elimina record"):
                cursor.execute("DELETE FROM spese WHERE id = ?", (record_id,))
                conn.commit()
                st.warning("Record eliminato.")
                st.rerun()

with mensili:
    if df.empty:
        st.warning("La tabella 'spese' è vuota.")
    else:
        # Filtri
        col1, col2 = st.columns(2)
        with col1:
            index_anno = anni.index(anno_corrente) if anno_corrente in anni else 0
            anno_sel_mensili = st.selectbox("Anno", anni, index=index_anno, key="anno_mensile")
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
        df_mensile = df_mensile[df_mensile['Data'].dt.year == int(anno_sel_mensili)]
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

        st.plotly_chart(fig_bar, use_container_width=True,
            config={
                "staticPlot": True  # 🔒 Disattiva ogni interazione
            }
        )



with annuali:
    if df.empty:
        st.warning("La tabella 'spese' è vuota.")
    else:
        # Filtri
        index_anno = anni.index(anno_corrente) if anno_corrente in anni else 0
        anno_sel_annuali = st.selectbox("Anno", anni, index=index_anno, key="anno_annuale")

        # Carica tutte le categorie con id
        cursor.execute("SELECT id, nome FROM categorie ORDER BY id")
        categorie_df = pd.DataFrame(cursor.fetchall(), columns=["id", "Categoria"])
        categorie_df["Categoria"] = categorie_df["Categoria"].str.capitalize()

        # Filtro spese
        df_anno = df.copy()
        df_anno['Categoria'] = df_anno['Categoria'].str.capitalize()
        df_anno = df_anno[df_anno['Data'].dt.year == int(anno_sel_annuali)]
        df_anno = df_anno[(df_anno['Da'] == st.session_state.user) | (
            (df_anno['Azione'] == 'Dividi') & (df_anno['Da'] != st.session_state.user)
        )]
        df_anno.loc[df_anno['Azione'].str.contains("Dividi", case=False, na=False), 'Euro'] /= 2

        # Totale per categoria
        spese_categoria = df_anno.groupby("Categoria")["Euro"].sum().reset_index()
        spese_completo = categorie_df.merge(spese_categoria, on="Categoria", how="left")
        spese_completo["Euro"] = spese_completo["Euro"].fillna(0).round(2)

        # Colori per necessarie (id < 12) e voluttuarie (id >= 12)
        spese_completo["Colore"] = spese_completo["id"].apply(
            lambda x: "#8ecae6" if x < 12 else "#ffb703"
        )

        # Statistiche
        # TODO inserire anche una statistica sul valore medio mensile per ogni variabile
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

        st.plotly_chart(fig_bar, use_container_width=True,
            config={
                "staticPlot": True
            }
        )

with overall:
    st.success("Olè")
    #utente_sel = st.selectbox("Da", utenti, key="utente_overall")
    # Implementa logica per tutte le spese...
    st.markdown(
    """
    - Aggregazione df spese per anno, mese, categoria
    - Per ogni categoria, grafico a barre x=mese, y=totale euro per visualizzare l'andamento nel tempo
    """
    )
    if df.empty:
        st.warning("La tabella 'spese' è vuota.")
    else:
        df_overall = df.copy()
        df_overall = df_overall[(df_overall['Da'] == st.session_state.user) | (
            (df_overall['Azione'] == 'Dividi') & (df_overall['Da'] != st.session_state.user)
        )]
        df_overall.loc[df_overall['Azione'].str.contains("Dividi", case=False, na=False), 'Euro'] /= 2
        df_overall['Categoria'] = df_overall['Categoria'].str.capitalize()
        # Prepara le colonne necessarie
        df_overall["Anno"] = df_overall["Data"].dt.year
        df_overall["Mese"] = df_overall["Data"].dt.month
        df_overall["DataPeriodo"] = pd.to_datetime(df_overall["Data"].dt.to_period("M").astype(str))
        
        # Aggrega le spese mensili per categoria
        spese_categoria_mensile = df_overall.groupby(["DataPeriodo", "Categoria"])["Euro"].sum().reset_index()

        # Loop per ogni categoria e mostrare grafico
        min_date = spese_categoria_mensile["DataPeriodo"].min()
        max_date = spese_categoria_mensile["DataPeriodo"].max()
        for cat in categorie:
            df_cat = spese_categoria_mensile[spese_categoria_mensile["Categoria"] == cat]

            # Calcola statistiche
            media = df_cat["Euro"].mean()
            mediana = df_cat["Euro"].median()
            std = df_cat["Euro"].std()

            # Mostra statistiche con formattazione
            st.markdown(f"### {cat}")
            st.markdown(
                f"- **Media:** € {media:.2f}  \n"
                f"- **Mediana:** € {mediana:.2f}  \n"
                f"- **Deviazione standard:** € {std:.2f}"
            )

            fig = px.bar(
                df_cat,
                x="DataPeriodo",
                y="Euro",
                labels={"DataPeriodo": "Mese", "Euro": "Totale speso (€)"},
                height=300
            )

            # Imposta limite asse x uguale per tutti
            fig.update_xaxes(
                tickformat="%b\n%Y",
                range=[min_date, max_date]
            )
            fig.update_layout(
                margin=dict(t=40, l=20, r=20, b=20),
                font=dict(size=14),
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)