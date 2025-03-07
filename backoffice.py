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
    new_project = st.text_input("Projeto:")  # Coluna 1
    new_id = st.text_input("ID da HU:")  # Coluna 2
    new_title = st.text_input("Título da HU:")  # Coluna 3
    new_link = st.text_input("Link do Confluence:")  # Coluna 7
    submit_button = st.form_submit_button("Cadastrar HU")
    
    if submit_button and new_id and new_title and new_link and new_project:
        # Gera o link de aprovação dinamicamente
        approval_link = f"https://aprovacao-de-hus.streamlit.app/?id={new_id}"
        
        # Adiciona a nova HU na planilha na ordem correta
        sheet.append_row([new_project, new_id, new_title, "Pendente", "", "", new_link, approval_link])
        st.success(f"{new_id} cadastrada com sucesso!")
        
        # Limpa o cache e recarrega os dados
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
    approved_count = hus[hus["Status"] == "Aprovado"].shape[0]
    rejected_count = hus[hus["Status"] == "Reprovado"].shape[0]
    adjustment_count = hus[hus["Status"] == "Ajuste Solicitado"].shape[0]
    
    # **Atualizar status na planilha**
    hu_index = hus.index[hus["ID_HU"] == selected_hu].tolist()[0] + 2  # Índice do Google Sheets
    sheet.update_cell(hu_index, 4, status)  # Coluna Status
    
    # **Layout organizado com colunas**
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader(hu_data['Título'])
        st.markdown(f"📂 **Projeto:** {hu_data.get('Projeto', 'Não informado')}")
        st.markdown(f"🔗 [Link Confluence]({hu_data['Link']})")
        st.markdown(f"📝 [Link para Aprovação]({hu_data['Link de Aprovação']})")
    
    with col2:
        st.markdown("### 📌 Status Atual")
        st.markdown(
            f"""
            <div style='background-color:#f4f4f4; padding:10px; border-radius:10px; text-align:center; font-size:18px; font-weight:bold; border: 2px solid {status_color}; color: {status_color};'>
                {status}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("---")
        st.metric("✔️ Aprovados", approved_count)
        st.metric("❌ Reprovados", rejected_count)
        st.metric("🔧 Ajustes Solicitados", adjustment_count)
