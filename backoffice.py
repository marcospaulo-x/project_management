import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configuração da página
st.set_page_config(page_title="Backoffice de Aprovação de HUs", layout="centered")

# Conectar ao Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(credentials)
SHEET_NAME = "Controle de HU's"
spreadsheet = client.open_by_key(st.secrets["spreadsheet"]["spreadsheet_id"])
sheet = spreadsheet.worksheet(SHEET_NAME)

# **Carregar os dados da planilha**
@st.cache_data
def load_hus():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df["ID_HU"] = df["ID_HU"].astype(str).str.strip()  # Garante que os IDs sejam strings
    return df

hus = load_hus()

# **Título**
st.title("Cadastro e Gerenciamento de Histórias de Usuários")

# **Formulário para adicionar nova HU**
st.subheader("Adicionar Nova HU")
with st.form(key="new_hu_form"):
    new_id = st.text_input("ID da HU:")
    new_title = st.text_input("Título da HU:")
    new_project = st.text_input("Projeto:")  # Novo campo para o projeto
    new_link = st.text_input("Link do Confluence:")    
    submit_button = st.form_submit_button("Cadastrar HU")
    
    if submit_button and new_id and new_title and new_link and new_project:
        sheet.append_row([new_id, new_title, new_link, new_project, "Pendente", "", "", ""])  # Adiciona projeto e status
        st.success(f"HU {new_id} cadastrada com sucesso!")
        st.experimental_rerun()

# **Dropdown para selecionar a HU**
selected_hu = st.selectbox("Selecione uma História de Usuário:", hus["ID_HU"])

# **Exibir detalhes da HU selecionada**
if selected_hu:
    hu_data = hus[hus["ID_HU"] == selected_hu].iloc[0]  # Obtém os detalhes da HU

    # **Definir cor do status**
    status_colors = {
        "Aprovado": "green",
        "Reprovado": "red",
        "Ajuste Solicitado": "orange",
        "Pendente": "gray"
    }
    status = hu_data["Status"]
    status_color = status_colors.get(status, "gray")  # Se não encontrar, usa cinza

    # **Exibir informações formatadas**
    st.markdown("""
        <style>
        .status-box {
            display: inline-block;
            padding: 12px 24px;
            color: white;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
            font-size: 18px;
            width: 200px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title(hu_data['Título'])
    st.markdown(f"**🔗 [Link Confluence]({hu_data['Link']})**")
    st.markdown(f"**📝 [Link para Aprovação](https://aprovacao-de-hus.streamlit.app/?id={hu_data['ID_HU']})**")
    st.markdown(f"**📂 Projeto: {hu_data.get('Projeto', 'Não informado')}**")  # Exibe o projeto
    
    # **Exibir status com destaque**
    st.markdown(
        f'<div class="status-box" style="background-color:{status_color};">📌 {status}</div>',
        unsafe_allow_html=True
    )