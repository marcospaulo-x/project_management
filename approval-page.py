import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configuração do Streamlit
st.set_page_config(page_title="Página de Aprovação de HU", layout="centered")

# Conectar ao Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(credentials)
SHEET_NAME = "HUs_Aprovacao"  # Nome da aba da planilha
spreadsheet = client.open_by_key(st.secrets["spreadsheet_id"])
sheet = spreadsheet.worksheet(SHEET_NAME)

# Função para carregar HUs
def load_hus():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Função para atualizar o status e observação da HU
def update_hu_status(hu_id, status, observacao):
    data = load_hus()
    index = data.index[data["ID"] == hu_id].tolist()
    
    if index:
        row = index[0] + 2  # Ajuste porque o índice do Google Sheets começa em 1 (mais cabeçalho)
        sheet.update_cell(row, data.columns.get_loc("Status") + 1, status)
        sheet.update_cell(row, data.columns.get_loc("Observação") + 1, observacao)
        return True
    return False

# Capturar o ID da HU via query parameter
query_params = st.query_params
hu_id = query_params.get("id", [""])[0]

if not hu_id:
    st.error("ID da HU não fornecido. Verifique o link e tente novamente.")
    st.stop()

# Carregar dados da HU específica
hus = load_hus()
hu_data = hus[hus["ID"] == hu_id]

if hu_data.empty:
    st.error("HU não encontrada.")
    st.stop()

hu_info = hu_data.iloc[0]

st.title("📝 Aprovação de História de Usuário")
st.write(f"**ID:** {hu_info['ID']}")
st.write(f"**Descrição:** {hu_info['Descrição']}")
st.markdown(f"[🔗 Link Confluence]({hu_info['Link Confluence']})")
st.write(f"**Status Atual:** {hu_info['Status']}")

# Formulário para aprovação ou reprovação
with st.form("approval_form"):
    status = st.radio("Selecione a ação:", ["Aprovar", "Aprovar com Observação", "Reprovar com Observação"])
    observacao = st.text_area("Observação (opcional)")
    submit = st.form_submit_button("Enviar Resposta")

    if submit:
        novo_status = "Aprovado" if status == "Aprovar" else "Aprovado com Observação" if status == "Aprovar com Observação" else "Reprovado"
        sucesso = update_hu_status(hu_id, novo_status, observacao)
        
        if sucesso:
            st.success("✅ Resposta enviada com sucesso!")
        else:
            st.error("❌ Erro ao atualizar a HU. Tente novamente.")
