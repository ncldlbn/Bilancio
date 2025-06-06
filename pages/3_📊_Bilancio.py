import streamlit as st

st.markdown(
"""

### TAB BILANCIO
- selettore mese e anno
- totale uscite del mese
    - spese necessarie (valore - percentuale rispetto entrate - scostamento dal valore target)
    - spese extra (valore - percentuale rispetto entrate - scostamento dal valore target)
- totale entrate
- totale risparmiato (valore - percentuale rispetto entrate - scostamento dal valore target)

### TAB SPESE EXTRA
- selettore anno
- tabella riepilogo spese extra per mese dell'anno in corso
    - tot spese extra per mese - budget residuo

### TAB DEBITO/CREDITO
Mostra se se in debito (-€ ...) o in credito (+€ ...) con l'altra persona

### TAB BUDGET
- input box per target necessarie
- input box per target risparmio
- input box per budget extra
"""
)