import streamlit as st
import pandas as pd
import datetime
import os
from domande import domande
from datetime import datetime as dt
from zoneinfo import ZoneInfo
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Configurazione della pagina
st.set_page_config(page_title="Test Carrelli Elevatori", layout="wide", page_icon="🦺")

# Stato iniziale
if "test_avviato" not in st.session_state:
    st.session_state.test_avviato = False

# Titolo
st.markdown("<h2 style='color:#00c3ff'>🦺 Test – Carrelli Elevatori Semoventi</h2>", unsafe_allow_html=True)

# FORM DATI PARTECIPANTE + MAIL
if not st.session_state.test_avviato:
    with st.form("dati_partecipante"):
        st.subheader("Dati del partecipante")
        nome = st.text_input("Nome e Cognome", max_chars=100)
        cf = st.text_input("Codice Fiscale (obbligatorio)", max_chars=16)
        azienda = st.text_input("Azienda")

        st.subheader("📨 RIFERIMENTI MAIL")
        mail_partecipante = st.text_input("📧 Email a cui inviare il test (può essere multipla, separata da virgole)", placeholder="es. mario.rossi@email.com, rspp@azienda.it")
        invia_copia_me = st.checkbox("✅ Invia copia anche a Simone Leandrini")

        accetto = st.checkbox("✅ Dichiaro di accettare il trattamento dei dati ai fini formativi (privacy)")
        avvia = st.form_submit_button("Inizia il test")

        if avvia:
            if not (nome and cf and azienda and accetto and mail_partecipante):
                st.error("Compila tutti i campi richiesti e accetta la privacy.")
            else:
                st.session_state.test_avviato = True
                st.session_state.nome = nome
                st.session_state.cf = cf.upper()
                st.session_state.azienda = azienda
                st.session_state.email_dest = [email.strip() for email in mail_partecipante.split(",")]
                if invia_copia_me:
                    st.session_state.email_dest.append("perindleandrini@4step.it")

# TEST
if st.session_state.test_avviato:
    risposte_utente = []
    punteggio = 0

    st.markdown("---")
    st.subheader("📋 Test – 15 domande a risposta multipla")

    for i, domanda in enumerate(domande):
        st.markdown(f"**Domanda {i+1}:** {domanda['testo']}")
        if "immagine" in domanda:
            if os.path.exists(domanda["immagine"]):
                st.image(domanda["immagine"], width=400)
            else:
                st.warning(f"⚠️ Immagine non trovata: {domanda['immagine']}")
        risposta = st.radio("Scegli la risposta:", domanda["opzioni"], key=f"q_{i}")
        risposte_utente.append(risposta)

    if st.button("Conferma e correggi il test"):
        st.markdown("---")
        st.subheader("📊 Risultato del test")

        for i, domanda in enumerate(domande):
            scelta = risposte_utente[i]
            corretta = domanda["opzioni"][domanda["risposta_corretta"]]
            if scelta == corretta:
                punteggio += 1
                st.success(f"✅ Domanda {i+1}: Corretta")
            else:
                st.error(f"❌ Domanda {i+1}: Errata – Risposta corretta: {corretta}")

        soglia = int(len(domande) * 0.8)
        superato = punteggio >= soglia
        st.markdown(f"### Totale corrette: **{punteggio}/{len(domande)}**")
        st.success("✅ Test superato!" if superato else "❌ Test NON superato")

        # Salvataggio risultato in Excel
        data_ora = dt.now(ZoneInfo("Europe/Rome")).strftime('%Y-%m-%d %H:%M')
        risultato = {
            "Data": data_ora,
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

        # Email con allegato
        sender = st.secrets["email"]["sender"]
        password = st.secrets["email"]["password"]

        corpo = f"""🧾 TEST COMPLETATO

📛 NOMINATIVO: {st.session_state.nome}
🆔 Codice Fiscale: {st.session_state.cf}
🏢 Azienda: {st.session_state.azienda}
🕒 Data/Ora: {data_ora}
📈 Punteggio: {punteggio}/{len(domande)}
📌 Esito: {'✅ SUPERATO' if superato else '❌ NON SUPERATO'}

📖 RISPOSTE DETTAGLIATE:
"""

        for i, domanda in enumerate(domande):
            testo = domanda["testo"]
            risposta_data = risposte_utente[i]
            corretta = domanda["opzioni"][domanda["risposta_corretta"]]
            esito = "✅ CORRETTA" if risposta_data == corretta else f"❌ ERRATA (Corretto: {corretta})"
            corpo += f"\nDomanda {i+1}: {testo}\nRisposta: {risposta_data} → {esito}\n"

        for destinatario in st.session_state.email_dest:
            msg = MIMEMultipart()
            msg["Subject"] = f"📩 Test Carrelli Elevatori – {st.session_state.nome}"
            msg["From"] = sender
            msg["To"] = destinatario

            msg.attach(MIMEText(corpo, "plain"))

            with open(file_path, "rb") as f:
                excel = MIMEApplication(f.read(), _subtype="xlsx")
                excel.add_header('Content-Disposition', 'attachment', filename="risultati_test.xlsx")
                msg.attach(excel)

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender, password)
                    server.send_message(msg)
                st.success(f"📤 Email inviata correttamente a: {destinatario}")
            except Exception as e:
                st.warning(f"❌ Errore nell'invio email a {destinatario}: {e}")
