# domande.py

import os

# Path assoluto alla cartella immagini
IMG_DIR = os.path.join(os.path.dirname(__file__), "immagini")

DOMANDE = [
    {
        "testo": "Quando deve essere effettuato il controllo giornaliero del carrello elevatore?",
        "opzioni": [
            "Solo a fine turno",
            "All’inizio del turno lavorativo",
            "Una volta a settimana"
        ],
        "corretta": 1
    },
    {
        "testo": "Come va affrontata una pendenza in discesa con carico?",
        "opzioni": [
            "Con il carico rivolto verso la discesa",
            "In retromarcia, con il carico a monte",
            "Con il carico sollevato per maggiore visibilità"
        ],
        "corretta": 1
    },
    {
        "testo": "Cosa rappresenta questa immagine?",
        "opzioni": [
            "Baricentro instabile con rischio di ribaltamento",
            "Baricentro stabile, condizioni corrette",
            "Carico eccentrico e instabile"
        ],
        "corretta": 1,
        "immagine": os.path.join(IMG_DIR, "baricentro_ok.png")
    },
    {
        "testo": "Cosa NON deve mai fare un operatore?",
        "opzioni": [
            "Spostare un carico senza visibilità",
            "Segnalare guasti al responsabile",
            "Guidare solo se abilitato"
        ],
        "corretta": 0
    },
    {
        "testo": "Qual è il documento che attesta la formazione obbligatoria per l’uso del carrello?",
        "opzioni": [
            "Patente B",
            "Attestato di abilitazione (Accordo Stato-Regioni)",
            "Certificato medico sportivo"
        ],
        "corretta": 1
    },
    {
        "testo": "Cosa indica questa immagine?",
        "opzioni": [
            "Posizione corretta in pendenza",
            "Pendenza errata",
            "Manovra consentita"
        ],
        "corretta": 1,
        "immagine": os.path.join(IMG_DIR, "pendenza_errata.png")
    },
    {
        "testo": "In caso di guasto al carrello, cosa si deve fare?",
        "opzioni": [
            "Continuare fino alla fine del turno",
            "Segnalare e fermare l’uso immediatamente",
            "Ripararlo da soli"
        ],
        "corretta": 1
    },
    {
        "testo": "Il carico deve essere:",
        "opzioni": [
            "Sollevato al massimo per sicurezza",
            "Appoggiato direttamente sulla cabina",
            "Stabile, centrato e ben fissato"
        ],
        "corretta": 2
    },
    {
        "testo": "Chi può condurre un carrello elevatore?",
        "opzioni": [
            "Chiunque abbia buona vista",
            "Solo chi ha frequentato un corso specifico",
            "Chi ha la patente di guida"
        ],
        "corretta": 1
    },
    {
        "testo": "Durante le manovre, l’operatore deve:",
        "opzioni": [
            "Parlare al cellulare per aggiornare il responsabile",
            "Indossare dispositivi di protezione e mantenere attenzione",
            "Aprire la porta laterale per visibilità"
        ],
        "corretta": 1
    },
    {
        "testo": "Le forche del carrello devono essere tenute:",
        "opzioni": [
            "Sollevate al massimo",
            "Sempre parallele al suolo e basse durante la marcia",
            "Inclinate all’indietro durante la guida"
        ],
        "corretta": 1
    },
    {
        "testo": "Cosa fare se una persona attraversa davanti al carrello?",
        "opzioni": [
            "Accelerare per passare prima",
            "Azionare il clacson e proseguire",
            "Fermarsi immediatamente e dare la precedenza"
        ],
        "corretta": 2
    },
    {
        "testo": "Cosa bisogna fare prima di usare un carrello ogni giorno?",
        "opzioni": [
            "Controllare visivamente e funzionalmente il mezzo",
            "Accenderlo e provarlo direttamente",
            "Pulirlo e lasciarlo acceso per scaldarlo"
        ],
        "corretta": 0
    },
    {
        "testo": "L’uso improprio del carrello può:",
        "opzioni": [
            "Essere utile per aumentare la produttività",
            "Causare incidenti gravi e danni a persone o cose",
            "Essere tollerato se si ha esperienza"
        ],
        "corretta": 1
    },
    {
        "testo": "Durante una curva il carrello va guidato:",
        "opzioni": [
            "Ad alta velocità per non rallentare la produzione",
            "A velocità ridotta per evitare ribaltamenti",
            "Con le forche alte per vedere meglio"
        ],
        "corretta": 1
    }
]
