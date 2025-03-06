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
        headers = sheet.row_values(1)  # Pega os cabeçalhos da planilha
        if "Projeto" not in headers:
            sheet.insert_row(["Projeto"], 1)  # Adiciona a coluna "Projeto" se não existir
        
        approval_link = f"https://aprovacao-de-hus.streamlit.app/?id={new_id}"
        
        sheet.append_row([new_project, new_id, new_title, "Pendente", "", "", new_link, approval_link])
        st.success(f"{new_id} cadastrada com sucesso!")
        
        st.cache_data.clear()
        hus = load_hus()

# **Dropdown para selecionar a HU**
selected_hu = st.selectbox("Selecione uma História de Usuário:", [""] + hus["ID_HU"].tolist())

# **Exibir detalhes da HU selecionada**
if selected_hu and selected_hu != "":
    hu_data = hus[hus["ID_HU"] == selected_hu].iloc[0]  # Obtém os detalhes da HU

    # **Contar os votos na planilha**
    status_counts = hus[hus["ID_HU"] == selected_hu]["Status"].value_counts()
    aprovados = status_counts.get("Aprovado", 0)
    reprovados = status_counts.get("Reprovado", 0)
    ajustes = status_counts.get("Ajuste Solicitado", 0)

    # **Determinar o novo status**
    status_votos = {
        "Aprovado": aprovados,
        "Reprovado": reprovados,
        "Ajuste Solicitado": ajustes
    }
    novo_status = max(status_votos, key=status_votos.get)  # Maioria dos votos define o status

    # **Atualizar na planilha se houver mudança**
    if novo_status != hu_data["Status"]:
        row_index = hus[hus["ID_HU"] == selected_hu].index[0] + 2  # Ajuste para linha correta
        sheet.update_cell(row_index, 4, novo_status)  # Atualiza a coluna 'Status'
        st.success(f"Status atualizado para: {novo_status}")

    # **Definir cor do status**
    status_colors = {
        "Aprovado": "green",
        "Reprovado": "red",
        "Ajuste Solicitado": "orange",
        "Pendente": "gray"
    }
    status = novo_status
    status_color = status_colors.get(status, "gray")

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
    st.markdown(f"**📂 Projeto: {hu_data.get('Projeto', 'Não informado')}**")  
    
    # **Exibir status com destaque**
    st.markdown(
        f'<div class="status-box" style="background-color:{status_color};">📌 {status}</div>',
        unsafe_allow_html=True
    )

    # **Exibir contagem de votos**
    st.markdown(f"✅ **Aprovados:** {aprovados}")
    st.markdown(f"❌ **Reprovados:** {reprovados}")
    st.markdown(f"🛠 **Ajuste Solicitado:** {ajustes}")
