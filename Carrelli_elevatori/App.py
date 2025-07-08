import streamlit as st
import pandas as pd
import datetime
import os
from domande import domande
from fpdf import FPDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Config pagina
st.set_page_config(page_title="Test Carrelli Elevatori", layout="wide", page_icon="🦺")

if "test_avviato" not in st.session_state:
    st.session_state.test_avviato = False

# PDF GENERATION
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "🦺 Report Test Carrelli Elevatori", 0, 1, "C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, "C")

def crea_pdf(nome, cf, azienda, punteggio, domande, risposte_utente):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "", 12)

    pdf.cell(0, 10, f"Nome: {nome}", ln=True)
    pdf.cell(0, 10, f"Codice Fiscale: {cf}", ln=True)
    pdf.cell(0, 10, f"Azienda: {azienda}", ln=True)
    pdf.cell(0, 10, f"Punteggio: {punteggio}/{len(domande)}", ln=True)
    pdf.ln(5)

    for i, domanda in enumerate(domande):
        scelta = risposte_utente[i]
        corretta = domanda["opzioni"][domanda["risposta_corretta"]]
        esito = "✅ Corretta" if scelta == corretta else f"❌ Errata (Corretto: {corretta})"
        pdf.set_text_color(0, 128, 0) if scelta == corretta else pdf.set_text_color(200, 0, 0)
        pdf.multi_cell(0, 10, f"Domanda {i+1}: {domanda['testo']}\nRisposta: {scelta}\n{esito}")
        pdf.ln(1)

    pdf.set_text_color(0, 0, 0)
    file_path = f"risultati/TEST_{cf}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.output(file_path)
    return file_path

# UI
st.markdown("<h2 style='color:#00c3ff'>🦺 Test – Carrelli Elevatori Semoventi</h2>", unsafe_allow_html=True)

if not st.session_state.test_avviato:
    with st.form("dati_partecipante"):
        st.subheader("Dati del partecipante")
        nome = st.text_input("Nome e Cognome")
        cf = st.text_input("Codice Fiscale (obbligatorio)")
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

if st.session_state.test_avviato:
    risposte_utente = []
    punteggio = 0

    st.markdown("---")
    st.subheader("📋 Test – 15 domande a risposta multipla")

    for i, domanda in enumerate(domande):
        st.markdown(f"**Domanda {i+1}:** {domanda['testo']}")
        if "immagine" in domanda and os.path.exists(domanda["immagine"]):
            st.image(domanda["immagine"], width=400)
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

        # Salvataggio Excel
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
        df_final = pd.concat([pd.read_excel(file_path), df], ignore_index=True) if os.path.exists(file_path) else df
        df_final.to_excel(file_path, index=False)
        st.info("📁 Risultati salvati correttamente.")

        # PDF allegato
        pdf_path = crea_pdf(st.session_state.nome, st.session_state.cf, st.session_state.azienda, punteggio, domande, risposte_utente)

        # Invio email
        sender = st.secrets["email"]["sender"]
        receiver = st.secrets["email"]["receiver"]
        password = st.secrets["email"]["password"]

        corpo = f"""🧾 TEST COMPLETATO

Nome: {st.session_state.nome}
Codice Fiscale: {st.session_state.cf}
Azienda: {st.session_state.azienda}
Data/Ora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
Punteggio: {punteggio}/{len(domande)}
Esito: {'✅ SUPERATO' if superato else '❌ NON SUPERATO'}

📋 Risposte:
"""
        for i, domanda in enumerate(domande):
            corpo += f"\nDomanda {i+1}: {domanda['testo']}\nRisposta: {risposte_utente[i]}\n"

        msg = MIMEMultipart()
        msg["Subject"] = f"📩 Test carrelli elevatori – {st.session_state.nome}"
        msg["From"] = sender
        msg["To"] = receiver
        msg.attach(MIMEText(corpo, "plain"))

        with open(pdf_path, "rb") as f:
            attach = MIMEApplication(f.read(), _subtype="pdf")
            attach.add_header("Content-Disposition", "attachment", filename=os.path.basename(pdf_path))
            msg.attach(attach)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender, password)
                server.send_message(msg)
            st.success("📤 Email inviata correttamente a 4Step con PDF allegato.")
        except Exception as e:
            st.warning(f"❌ Errore nell'invio dell'email: {e}")
