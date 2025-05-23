import streamlit as st
import requests

url = "https://n8n.fortop.it/webhook/8a7ad845-fac9-45ae-89e1-0f3c6cf29522/chat"

st.title("💬 Lucio AI")

query = st.text_input("Scrivi la tua richiesta")

if st.button("Invia"):
    payload = {"chatInput": query}
    response = requests.post(url, json=payload)
    if response.ok:
        st.success("✅ Risposta ricevuta:")
        st.write(response.text)
    else:
        st.error(f"Errore: {response.status_code}")
