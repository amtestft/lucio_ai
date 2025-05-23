import streamlit as st
import requests
from fastapi import FastAPI, Request
import threading
import uvicorn

# Configurazione
N8N_CHAT_URL = "https://n8n.fortop.it/webhook/8a7ad845-fac9-45ae-89e1-0f3c6cf29522/chat"
N8N_APPROVAL_URL = "https://n8n.fortop.it/webhook/approva-mail"

# Sessione utente
session_id = "user-session-001"

# Start FastAPI backend per ricevere draft
app = FastAPI()
drafts = {}

@app.post("/api/draft")
async def receive_draft(req: Request):
    data = await req.json()
    drafts[data["sessionId"]] = data
    return {"status": "received"}

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

threading.Thread(target=run_api, daemon=True).start()

# Interfaccia Streamlit
st.set_page_config(page_title="Lucio AI - Assistente Finanza", layout="centered")
st.title("💬 Lucio AI – Assistenza Finanziaria")

query = st.text_input("Scrivi la tua richiesta")

if st.button("Invia"):
    with st.spinner("Invio al workflow n8n..."):
        payload = {
            "chatInput": query,
            "sessionId": session_id
        }
        response = requests.post(N8N_CHAT_URL, json=payload)
        if response.ok:
            st.success("✅ Richiesta inviata. Attendi la bozza...")

# Mostra la bozza se disponibile
if session_id in drafts:
    draft = drafts[session_id]
    st.markdown("### ✉️ Bozza generata da Lucio")
    st.text_input("Destinatario", draft["to"], disabled=True)
    st.text_input("Oggetto", draft["subject"], disabled=True)
    st.text_area("Testo Email", draft["draft"], height=200, disabled=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Approva e Invia"):
            payload = {
                "approved": True,
                "to": draft["to"],
                "subject": draft["subject"],
                "body": draft["draft"]
            }
            res = requests.post(N8N_APPROVAL_URL, json=payload)
            if res.ok:
                st.success("✅ Email inviata con successo.")
                del drafts[session_id]
            else:
                st.error("❌ Errore durante l'invio dell'approvazione.")

    with col2:
        if st.button("❌ Rifiuta"):
            st.warning("❎ Email non inviata.")
            del drafts[session_id]
