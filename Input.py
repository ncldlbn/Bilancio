import streamlit as st
import sqlite3
import datetime

# --- Connessione al DB ---
conn = sqlite3.connect("spese.db", check_same_thread=False)
cursor = conn.cursor()

# # --- Funzione login (password in chiaro) ---
# def login(username, password):
#     cursor.execute("SELECT password FROM utenti WHERE username = ?", (username,))
#     row = cursor.fetchone()
#     if row and password == row[0]:
#         return True
#     return False

# # --- Sessione ---
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
#     st.session_state.user = ""

# # --- Login UI ---
# if not st.session_state.logged_in:
#     st.title("Login")
#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")

#     if st.button("Login"):
#         if login(username, password):
#             st.session_state.logged_in = True
#             st.session_state.user = username
#             st.success("Login effettuato!")
#             st.rerun()
#         else:
#             st.error("Credenziali non valide.")
#     st.stop()

# # --- Logout UI ---
# st.sidebar.write(f"👋 Ciao, {st.session_state.user}")
# if st.sidebar.button("Logout", use_container_width=True):
#     st.session_state.logged_in = False
#     st.session_state.user = ""
#     st.rerun()

# --- Dashboard: Inserimento Spese ---
st.title("Input")

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

oggi = datetime.date.today()


spese, entrate = st.tabs(["💸 Spese", "💰 Entrate"])

with spese:
    st.write(f"Utente: {st.session_state.user}")
    data = st.date_input("Data", oggi)
    euro = st.number_input("Euro", min_value=0.0, step=0.01, format="%.2f")
    #da_ = st.selectbox("Da", ["Nicola", "Martina"])
    #da_ = st.selectbox("Da", ["Nicola", "Martina"], index=["Nicola", "Martina"].index(st.session_state.user) if st.session_state.user in ["Nicola", "Martina"] else 0)
    da_ = st.session_state.user
    tipo_categoria = st.radio("Tipo di spesa", ["Necessaria", "Extra"], horizontal=True)

    cursor.execute("SELECT nome FROM categorie WHERE tipo = ? ORDER BY id ASC", (tipo_categoria,))
    categorie = [""] + [row[0] for row in cursor.fetchall()]
    categoria = st.selectbox("Categoria", categorie)

    descrizione = st.text_input("Descrizione")
    azione = st.selectbox("Azione", ["", "Dividi", "Dai", "Saldo"])

    if st.button("Aggiungi spesa", use_container_width=True):
        if descrizione.strip() == "":
            st.error("Inserisci una descrizione.")
        elif categoria == "":
            st.error("Seleziona una categoria.")
        else:
            cursor.execute("""
            INSERT INTO spese (data, euro, da, descrizione, categoria, azione)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (data.strftime("%d/%m/%Y"), euro, da_, descrizione, categoria, azione))
            conn.commit()
            st.toast("💸 Spesa inserita!")


with entrate:
    st.write(f"Utente: {st.session_state.user}")
    data = st.date_input("Data", oggi, key="data_entrate")
    euro = st.number_input("Euro", min_value=0.0, step=0.01, format="%.2f", key="euro_entrate")
    #da_ = st.selectbox("Da", ["Nicola", "Martina"], key="da_entrate")
    da_ = st.session_state.user
    descrizione = st.text_input("Descrizione", key="descrizione_entrate")

    if st.button("Aggiungi Entrata", use_container_width=True, key="btn_entrate"):
        if descrizione.strip() == "":
            st.error("Inserisci una descrizione.")
        else:
            # cursor.execute("""
            #     INSERT INTO spese (data, euro, da, descrizione, categoria, azione)
            #     VALUES (?, ?, ?, ?, ?, ?)
            # """, (data.strftime("%d/%m/%Y"), euro, da_, descrizione, categoria, azione))
            # conn.commit()
            st.toast("Entrata aggiunta con successo!")