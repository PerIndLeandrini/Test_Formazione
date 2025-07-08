import streamlit as st
import pandas as pd
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from domande import domande

st.set_page_config(page_title="Test Carrelli Elevatori", layout="wide", page_icon="🪺")

if "test_avviato" not in st.session_state:
    st.session_state.test_avviato = False

st.markdown("<h2 style='color:#00c3ff'>🪧 Test – Carrelli Elevatori Semoventi</h2>", unsafe_allow_html=True)

if not st.session_state.test_avviato:
    with st.form("dati_partecipante"):
        st.subheader("Dati del partecipante")
        nome = st.text_input("Nome e Cognome", max_chars=100)
        cf = st.text_input("Codice Fiscale (obbligatorio)", max_chars=16)
        azienda = st.text_input("Azienda")

        st.subheader("📧 RIFERIMENTI MAIL")
        email_partecipante = st.text_input("Email partecipante (obbligatoria)")
        email_altre = st.text_input("Altre email per copia test (separate da virgola, opzionali)")
        copia_simone = st.checkbox("Inviare copia anche a Simone Leandrini?")

        accetto = st.checkbox("✅ Dichiaro di accettare il trattamento dei dati ai fini formativi (privacy)")
        avvia = st.form_submit_button("Inizia il test")

        if avvia:
            if not (nome and cf and azienda and accetto and email_partecipante):
                st.error("Compila tutti i campi richiesti e accetta la privacy.")
            else:
                st.session_state.test_avviato = True
                st.session_state.nome = nome
                st.session_state.cf = cf.upper()
                st.session_state.azienda = azienda
                st.session_state.email_partecipante = email_partecipante
                st.session_state.email_altre = email_altre
                st.session_state.copia_simone = copia_simone

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
        esito = "✅ SUPERATO" if superato else "❌ NON SUPERATO"
        st.markdown(f"### Totale corrette: **{punteggio}/{len(domande)}**")
        st.success("Test superato!" if superato else "Test NON superato")

        # Salva in Excel
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
        file_path = f"risultati/{st.session_state.cf}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        df.to_excel(file_path, index=False)
        st.info(f"📁 Risultati salvati in `{file_path}`.")

        # Componi lista email destinatari
        destinatari = [st.session_state.email_partecipante]
        if st.session_state.email_altre:
            destinatari += [e.strip() for e in st.session_state.email_altre.split(",") if e.strip()]
        if st.session_state.copia_simone:
            destinatari.append("perindleandrini@4step.it")

        # Componi email
        sender = st.secrets["email"]["sender"]
        password = st.secrets["email"]["password"]

        msg = MIMEMultipart()
        msg["Subject"] = f"📧 Test carrelli elevatori – {st.session_state.nome}"
        msg["From"] = sender
        msg["To"] = ", ".join(destinatari)

        corpo = f"""
📄 TEST COMPLETATO

NOMINATIVO: {st.session_state.nome}
Codice Fiscale: {st.session_state.cf}
Azienda: {st.session_state.azienda}
Data/Ora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
Punteggio: {punteggio}/{len(domande)}
Esito: {esito}
"""
        for i, domanda in enumerate(domande):
            corretta = domanda["opzioni"][domanda["risposta_corretta"]]
            scelta = risposte_utente[i]
            simbolo = "✅" if scelta == corretta else "❌"
            corpo += f"\n{simbolo} Domanda {i+1}: {domanda['testo']}\nRisposta data: {scelta}\nRisposta corretta: {corretta}\n"

        msg.attach(MIMEText(corpo, "plain"))

        with open(file_path, "rb") as f:
            attachment = MIMEApplication(f.read(), _subtype="xlsx")
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
            msg.attach(attachment)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender, password)
                server.sendmail(sender, destinatari, msg.as_string())
            st.success("Email inviata correttamente ai destinatari indicati.")
        except Exception as e:
            st.warning(f"Errore invio email: {e}")
