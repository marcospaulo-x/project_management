import streamlit as st
import pandas as pd
import os
from google.oauth2.service_account import Credentials

def get_gcp_credentials():
    return Credentials.from_service_account_info(
        {
            "type": "service_account",
            "project_id": st.secrets["gcp"]["project_id"],
            "private_key_id": st.secrets["gcp"]["private_key_id"],
            "private_key": st.secrets["gcp"]["private_key"],
            "client_email": st.secrets["gcp"]["client_email"],
            "client_id": st.secrets["gcp"]["client_id"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": st.secrets["gcp"]["client_x509_cert_url"]
        }
    )

st.set_page_config(page_title="Backoffice - Acompanhamento de HUs", layout="centered")
CSV_FILE = "./hus.csv"

# Função para carregar as HUs do arquivo CSV
def load_hus():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE).to_dict(orient="records")
    return []

# Função para salvar as HUs no arquivo CSV
def save_hus(hus):
    pd.DataFrame(hus).to_csv(CSV_FILE, index=False)

# Carregar HUs ao iniciar
st.session_state.hus = load_hus()

st.title("📌 Acompanhamento de HUs e Aprovação")

# Formulário para adicionar HUs
with st.form("nova_hu"):
    hu_id = st.text_input("ID da HU")
    descricao = st.text_area("Descrição da HU")
    link_confluence = st.text_input("Link do Confluence")
    submit = st.form_submit_button("Adicionar HU")

    if submit:
        if hu_id and descricao and link_confluence:
            link_aprovacao = f"http://localhost:8502/?id={hu_id}"
            nova_hu = {
                "ID": hu_id,
                "Descrição": descricao,
                "Link Confluence": link_confluence,
                "Link Aprovação": link_aprovacao,
                "Status": "Pendente",
                "Observação": ""
            }
            st.session_state.hus.append(nova_hu)
            save_hus(st.session_state.hus)
            st.success("✅ HU adicionada com sucesso!")
        else:
            st.error("⚠️ Todos os campos são obrigatórios!")

# Exibição das HUs cadastradas
st.write("## 📜 Histórias de Usuário Cadastradas")
if st.session_state.hus:
    for hu in st.session_state.hus:
        st.write(f"**ID:** {hu['ID']}")
        st.write(f"**Descrição:** {hu['Descrição']}")
        st.markdown(f"[🔗 Link Confluence]({hu['Link Confluence']})")
        st.markdown(f"[📝 Link para Aprovação]({hu['Link Aprovação']})")
        st.write(f"**Status:** {hu['Status']}")
        st.write("---")
else:
    st.info("Nenhuma HU cadastrada ainda.")
