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
    df["ID_HU"] = df["ID_HU"].astype(str).str.strip()
    return df

hus = load_hus()

# **Título**
st.title("Cadastro e Gerenciamento de Histórias de Usuários")

# **Formulário para adicionar nova HU**
st.subheader("Adicionar Nova HU")
with st.form(key="new_hu_form"):
    new_id = st.text_input("ID da HU:")
    new_title = st.text_input("Título da HU:")
    new_project = st.text_input("Projeto:")
    new_link = st.text_input("Link do Confluence:")    
    submit_button = st.form_submit_button("Cadastrar HU")
    
    if submit_button and new_id and new_title and new_link and new_project:
        headers = sheet.row_values(1)
        if "Projeto" not in headers:
            sheet.insert_row(["Projeto"], 1)
        
        approval_link = f"https://aprovacao-de-hus.streamlit.app/?id={new_id}"
        
        sheet.append_row([new_project, new_id, new_title, "Pendente", "", "", new_link, approval_link])
        st.success(f"{new_id} cadastrada com sucesso!")
        
        st.cache_data.clear()
        hus = load_hus()

# **Dropdown para selecionar a HU**
selected_hu = st.selectbox("Selecione uma História de Usuário:", [""] + hus["ID_HU"].tolist())

# **Exibir detalhes da HU selecionada**
if selected_hu and selected_hu != "":
    hu_data = hus[hus["ID_HU"] == selected_hu].iloc[0]

    # **Definir cor do status**
    status_colors = {
        "Aprovado": "#28a745",
        "Reprovado": "#dc3545",
        "Ajuste Solicitado": "#ffc107",
        "Pendente": "#6c757d"
    }
    status = hu_data["Status"]
    status_color = status_colors.get(status, "#6c757d")
    
    # **Contagem de aprovações**
    filtered_data = hus[hus["ID_HU"] == selected_hu]
    approved_count = (filtered_data["Status"] == "Aprovado").sum()
    rejected_count = (filtered_data["Status"] == "Reprovado").sum()
    adjustment_count = (filtered_data["Status"] == "Ajuste Solicitado").sum()
    
    # **Atualiza o status com base nos votos**
    if approved_count > max(rejected_count, adjustment_count):
        new_status = "Aprovado"
    elif rejected_count > max(approved_count, adjustment_count):
        new_status = "Reprovado"
    elif adjustment_count > max(approved_count, rejected_count):
        new_status = "Ajuste Solicitado"
    else:
        new_status = "Pendente"
    
    if new_status != status:
        sheet.update_cell(filtered_data.index[0] + 2, 4, new_status)
        status = new_status
    
    # **Exibir informações formatadas**
    st.markdown(f"""
        <style>
        .status-box {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 15px;
            color: white;
            border-radius: 8px;
            font-weight: bold;
            font-size: 18px;
            background-color: {status_color};
        }}
        .counter-box {{
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 16px;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"## {hu_data['Título']}")
    st.markdown(f"**📂 Projeto: {hu_data.get('Projeto', 'Não informado')}**")
    st.markdown(f"🔗 [Link Confluence]({hu_data['Link']})")
    st.markdown(f"📝 [Link para Aprovação](https://aprovacao-de-hus.streamlit.app/?id={hu_data['ID_HU']})")
    
    st.markdown(f'<div class="status-box">📌 {status}</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="counter-box">✅ Aprovados: {approved_count}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="counter-box">❌ Reprovados: {rejected_count}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="counter-box">⚠️ Ajuste Solicitado: {adjustment_count}</div>', unsafe_allow_html=True)
