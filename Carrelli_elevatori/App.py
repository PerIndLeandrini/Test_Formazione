import streamlit as st
import pandas as pd
import datetime
import os
from domande import domande
from PIL import Image, ImageDraw, ImageFont
import textwrap
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# Config pagina
st.set_page_config(page_title="Test Carrelli Elevatori", layout="wide", page_icon="🦺")

if "test_avviato" not in st.session_state:
    st.session_state.test_avviato = False

st.markdown("<h2 style='color:#00c3ff'>🦺 Test – Carrelli Elevatori Semoventi</h2>", unsafe_allow_html=True)

# FORM PARTECIPANTE
if not st.session_state.test_avviato:
    with st.form("dati_partecipante"):
        st.subheader("Dati del partecipante")
        nome = st.text_input("Nome e Cognome", max_chars=100)
        cf = st.text_input("Codice Fiscale (obbligatorio)", max_chars=16)
        azienda = st.text_input("Azienda")
        accetto = st.checkbox("✅ Accetto il trattamento dei dati ai fini formativi (privacy)")
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

        # Salva Excel
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
        st.info("📁 Risultati salvati in `risultati/risultati_test.xlsx`.")

        # === CREAZIONE IMMAGINE TEST ===
        def crea_immagine_test(nome, cf, azienda, punteggio, domande, risposte_utente):
            width, height = 1200, 1800 + len(domande)*50
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)

            try:
                font_title = ImageFont.truetype("arial.ttf", 36)
                font_text = ImageFont.truetype("arial.ttf", 20)
            except:
                font_title = font_text = ImageFont.load_default()

            y = 20
            draw.text((width//2 - 200, y), "Riepilogo Test Carrelli Elevatori", fill="black", font=font_title)
            y += 60
            draw.text((50, y), f"Nome: {nome}", fill="black", font=font_text); y += 30
            draw.text((50, y), f"Codice Fiscale: {cf}", fill="black", font=font_text); y += 30
            draw.text((50, y), f"Azienda: {azienda}", fill="black", font=font_text); y += 30
            draw.text((50, y), f"Punteggio: {punteggio}/{len(domande)}", fill="black", font=font_text); y += 30
            draw.text((50, y), "Esito: " + ("SUPERATO" if punteggio >= int(len(domande)*0.8) else "NON SUPERATO"),
                      fill="green" if punteggio >= int(len(domande)*0.8) else "red", font=font_text)
            y += 50

            for i, domanda in enumerate(domande):
                testo = f"{i+1}. {domanda['testo']}"
                risposta = risposte_utente[i]
                corretta = domanda["opzioni"][domanda["risposta_corretta"]]
                colore = "green" if risposta == corretta else "red"
                wrap_testo = textwrap.fill(testo, width=100)

                draw.text((50, y), wrap_testo, fill="black", font=font_text); y += 40
                draw.text((80, y), f"Risposta data: {risposta}", fill=colore, font=font_text); y += 30
                if risposta != corretta:
                    draw.text((80, y), f"Risposta corretta: {corretta}", fill="blue", font=font_text); y += 30
                y += 10

            os.makedirs("report_img", exist_ok=True)
            img_path = f"report_img/test_{cf}.png"
            img.save(img_path)
            return img_path

        img_path = crea_immagine_test(
            st.session_state.nome,
            st.session_state.cf,
            st.session_state.azienda,
            punteggio,
            domande,
            risposte_utente
        )

        # === INVIO EMAIL CON IMMAGINE ===
        sender = st.secrets["email"]["sender"]
        receiver = st.secrets["email"]["receiver"]
        password = st.secrets["email"]["password"]

        msg = MIMEMultipart()
        msg["Subject"] = f"Test carrelli elevatori – {st.session_state.nome}"
        msg["From"] = sender
        msg["To"] = receiver

        corpo = f"""
🧾 TEST COMPLETATO

Nome: {st.session_state.nome}
Codice Fiscale: {st.session_state.cf}
Azienda: {st.session_state.azienda}
Data/Ora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
Punteggio: {punteggio}/{len(domande)}
Esito: {"✅ SUPERATO" if superato else "❌ NON SUPERATO"}

In allegato trovi il riepilogo visivo del test.
"""
        msg.attach(MIMEText(corpo, "plain"))

        with open(img_path, "rb") as f:
            img_part = MIMEImage(f.read(), name=os.path.basename(img_path))
            msg.attach(img_part)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender, password)
                server.sendmail(sender, receiver, msg.as_string())
            st.success("📤 Email inviata con allegato immagine.")
        except Exception as e:
            st.warning(f"❌ Errore nell'invio dell'email: {e}")
