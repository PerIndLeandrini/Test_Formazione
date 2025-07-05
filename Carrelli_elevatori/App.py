# app.py

import streamlit as st
import pandas as pd
import datetime
import os
from domande import DOMANDE

# Configurazione della pagina
st.set_page_config(page_title="Test Carrelli Elevatori", layout="wide", page_icon="🦺")

# Stato persistente
if "test_avviato" not in st.session_state:
    st.session_state.test_avviato = False

# Titolo principale
st.markdown("<h2 style='color:#00c3ff'>🦺 Test – Carrelli Elevatori Semoventi</h2>", unsafe_allow_html=True)

# FORM INIZIALE – DATI PARTECIPANTE
if not st.session_state.test_avviato:
    with st.form("dati_partecipante"):
        st.subheader("Dati del partecipante")
        nome = st.text_input("Nome e Cognome", max_chars=100)
        cf = st.text_input("Codice Fiscale (obbligatorio)", max_chars=16)
        azienda = st.text_input("Azienda")
        accetto = st.checkbox("✅ Dichiaro di accettare il trattamento dei dati ai fini formativi (privacy)")
        avvia = st.form_submit_button("Inizia il test")

        if avvia:
            if not (nome and cf and azienda and accetto):
                st.error("Compila tutti i campi richiesti e accetta la privacy.")
            else:
                st.session_state.test_avviato = True
                st.session_state.nome = nome
                st.session_state.cf = cf.upper()
                st.session_state.azienda = azienda

# SEZIONE TEST
if st.session_state.test_avviato:
    risposte_utente = []
    punteggio = 0

    st.markdown("---")
    st.subheader("📋 Test – 15 domande a risposta multipla")

    for i, domanda in enumerate(DOMANDE):
        st.markdown(f"**Domanda {i+1}:** {domanda['testo']}")
        if "immagine" in domanda:
            st.image(domanda["immagine"], width=400)
        risposta = st.radio("Scegli la risposta:", domanda["opzioni"], key=f"q_{i}")
        risposte_utente.append(risposta)

    if st.button("Conferma e correggi il test"):
        st.markdown("---")
        st.subheader("📊 Risultato del test")

        for i, domanda in enumerate(DOMANDE):
            scelta = risposte_utente[i]
            corretta = domanda["opzioni"][domanda["corretta"]]
            if scelta == corretta:
                punteggio += 1
                st.success(f"✅ Domanda {i+1}: Corretta")
            else:
                st.error(f"❌ Domanda {i+1}: Errata – Risposta corretta: {corretta}")

        soglia = int(len(DOMANDE) * 0.8)
        superato = punteggio >= soglia
        st.markdown(f"### Totale corrette: **{punteggio}/{len(DOMANDE)}**")
        st.success("✅ Test superato!" if superato else "❌ Test NON superato")

        # Salvataggio risultato
        risultato = {
            "Data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Nome": st.session_state.nome,
            "Codice Fiscale": st.session_state.cf,
            "Azienda": st.session_state.azienda,
            "Punteggio": punteggio,
            "Esito": "Superato" if superato else "Non superato"
        }

        for i, r in enumerate(risposte_utente):
            risultato[f"Domanda_{i+1}"] = r

        df = pd.DataFrame([risultato])
        os.makedirs("risultati", exist_ok=True)
        file_path = "risultati/risultati_test.xlsx"

        if os.path.exists(file_path):
            df_exist = pd.read_excel(file_path)
            df_final = pd.concat([df_exist, df], ignore_index=True)
        else:
            df_final = df

        df_final.to_excel(file_path, index=False)
        st.info("📁 Risultati salvati correttamente in `risultati/risultati_test.xlsx`.")