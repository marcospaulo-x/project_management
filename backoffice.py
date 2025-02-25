import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Backoffice - Acompanhamento de HUs", layout="centered")

# Conectar ao Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(credentials)
SHEET_NAME = "Controle de HU's"
spreadsheet = client.open_by_key(st.secrets["spreadsheet"]["spreadsheet_id"])
sheet = spreadsheet.worksheet(SHEET_NAME)

# URL correta para a página de aprovação
APPROVAL_URL = "https://aprovacao-de-hus.streamlit.app/"

# Função para carregar HUs da planilha
def load_hus():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Função para salvar nova HU na planilha
def save_hu(hu_id, titulo, link_confluence):
    hu_data = load_hus()

    # Gerar link de aprovação correto
    link_aprovacao = f"{APPROVAL_URL}?id={hu_id}"  

    # Adicionar nova linha na planilha
    sheet.append_row([hu_id, titulo, "Pendente", "", "", link_confluence, link_aprovacao])

    return link_aprovacao

# Interface do Backoffice
st.title("📌 Acompanhamento de HUs e Aprovação")

with st.form("nova_hu"):
    hu_id = st.text_input("ID da HU")
    titulo = st.text_input("Título da HU")
    link_confluence = st.text_input("Link do Confluence")
    submit = st.form_submit_button("Adicionar HU")

    if submit:
        if hu_id and titulo and link_confluence:
            link_aprovacao = save_hu(hu_id, titulo, link_confluence)
            st.success(f"✅ HU adicionada com sucesso!\n[📝 Link para Aprovação]({link_aprovacao})")
        else:
            st.error("⚠️ Todos os campos são obrigatórios!")

# Exibição das HUs cadastradas
st.write("## 📜 Histórias de Usuário Cadastradas")
hus = load_hus()
if not hus.empty:
    for _, hu in hus.iterrows():
        st.write(f"**ID:** {hu['ID_HU']}")  # Ajustado para a nomenclatura correta
        st.write(f"**Título:** {hu['Título']}")
        st.markdown(f"[🔗 Link Confluence]({hu['Link']})")
        st.markdown(f"[📝 Link para Aprovação]({hu['Link']})")  # Agora pega o link correto da planilha
        st.write(f"**Status:** {hu['Status']}")
        st.write("---")
else:
    st.info("Nenhuma HU cadastrada ainda.")
