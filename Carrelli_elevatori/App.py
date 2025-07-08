import streamlit as st
import pandas as pd
import datetime
import os
from domande import domande
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Configurazione della pagina
st.set_page_config(page_title="Test Carrelli Elevatori", layout="wide", page_icon="🪺")

# Stato persistente
if "test_avviato" not in st.session_state:
    st.session_state.test_avviato = False

# Titolo principale
st.markdown("<h2 style='color:#00c3ff'>🪺 Test – Carrelli Elevatori Semoventi</h2>", unsafe_allow_html=True)

# FORM INIZIALE
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

        # Salvataggio risultato Excel
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
        st.info("Risultati salvati in risultati/risultati_test.xlsx")

        # Invio email HTML + allegato Excel
        sender = st.secrets["email"]["sender"]
        receiver = st.secrets["email"]["receiver"]
        password = st.secrets["email"]["password"]

        msg = MIMEMultipart()
        msg["Subject"] = f"📩 Test carrelli elevatori – {st.session_state.nome}"
        msg["From"] = sender
        msg["To"] = receiver

        # Corpo HTML
        html = f"""
        <h3>📅 TEST COMPLETATO</h3>
        <b>NOMINATIVO:</b> {st.session_state.nome}<br>
        <b>Codice Fiscale:</b> {st.session_state.cf}<br>
        <b>Azienda:</b> {st.session_state.azienda}<br>
        <b>Data/Ora:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}<br>
        <b>Punteggio:</b> {punteggio}/{len(domande)}<br>
        <b>Esito:</b> {'<span style="color:green">✅ SUPERATO</span>' if superato else '<span style="color:red">❌ NON SUPERATO</span>'}<br><hr>
        <h4>📒 Domande e risposte fornite:</h4>
        """

        for i, domanda in enumerate(domande):
            testo = domanda["testo"]
            risposta_data = risposte_utente[i]
            risposta_corretta = domanda["opzioni"][domanda["risposta_corretta"]]
            if risposta_data == risposta_corretta:
                colore = "green"
                emoji = "✅"
                correzione = ""
            else:
                colore = "red"
                emoji = "❌"
                correzione = f"<br><b>Risposta corretta:</b> {risposta_corretta}"
            html += f"<p><b>Domanda {i+1}:</b> {testo}<br><span style='color:{colore}'>{emoji} Risposta data: {risposta_data}</span>{correzione}</p>"

        msg.attach(MIMEText(html, "html"))

        # Allegato Excel
        with open(file_path, "rb") as f:
            part = MIMEApplication(f.read(), _subtype="xlsx")
            part.add_header('Content-Disposition', 'attachment', filename="risultati_test.xlsx")
            msg.attach(part)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender, password)
                server.sendmail(sender, receiver, msg.as_string())
            st.success("📤 Email inviata correttamente con allegato.")
        except Exception as e:
            st.warning(f"❌ Errore invio email: {e}")
