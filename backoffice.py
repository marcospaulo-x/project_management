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

def get_majority_status(hus, hu_id):
    hu_votes = hus[hus["ID_HU"] == hu_id]
    if hu_votes.empty:
        return "Pendente"
    status_counts = hu_votes["Status"].value_counts()
    return status_counts.idxmax()  # Retorna o status com mais votos

def get_vote_counts(hus, hu_id):
    hu_votes = hus[hus["ID_HU"] == hu_id]
    approved_count = hu_votes[hu_votes["Status"] == "Aprovado"].shape[0]
    rejected_count = hu_votes[hu_votes["Status"] == "Reprovado"].shape[0]
    adjustment_count = hu_votes[hu_votes["Status"] == "Ajuste Solicitado"].shape[0]
    return approved_count, rejected_count, adjustment_count

def get_stakeholders_and_justifications(hus, hu_id):
    hu_votes = hus[hus["ID_HU"] == hu_id]
    stakeholders = ", ".join(hu_votes["Stakeholder Aprovador"].dropna().tolist())
    justifications = "\n".join(hu_votes["Observação"].dropna().tolist())
    return stakeholders, justifications

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
        # Gera o link de aprovação dinamicamente
        approval_link = f"https://aprovacao-de-hus.streamlit.app/?id={new_id}"
        
        # Adiciona a nova HU na planilha na ordem correta
        sheet.append_row([new_project, new_id, new_title, "Pendente", "", "", new_link, approval_link])
        st.success(f"{new_id} cadastrada com sucesso!")
        
        # Limpa o cache e recarrega os dados
        st.cache_data.clear()
        hus = load_hus()

# **Recarregar os dados da planilha**
hus = load_hus()

# **Dropdown para selecionar a HU**
selected_hu = st.selectbox("Selecione uma História de Usuário:", [""] + hus["ID_HU"].drop_duplicates().tolist())

# **Exibir detalhes da HU selecionada**
if selected_hu and selected_hu != "":
    # **Recarregar os dados da planilha para garantir que estejam atualizados**
    hus = load_hus()
    
    # **Definir hu_data**
    hu_data = hus[hus["ID_HU"] == selected_hu].iloc[0]  # Obtém os detalhes da HU selecionada
    
    # **Obter status majoritário e contagem de votos**
    status = get_majority_status(hus, selected_hu)
    approved_count, rejected_count, adjustment_count = get_vote_counts(hus, selected_hu)
    stakeholders, justifications = get_stakeholders_and_justifications(hus, selected_hu)
    
    # **Definir cor do status**
    status_colors = {
        "Aprovado": "#28a745",
        "Reprovado": "#dc3545",
        "Ajuste Solicitado": "#ffc107",
        "Pendente": "#6c757d"
    }
    status_color = status_colors.get(status, "#6c757d")
    
    # **Layout organizado com colunas**
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader(hu_data['Título'])
        st.markdown(f"📂 **Projeto:** {hu_data.get('Projeto', 'Não informado')}")
        st.markdown(f"🔗 [Link Confluence]({hu_data['Link']})")
        st.markdown(f"📝 [Link para Aprovação](https://aprovacao-de-hus.streamlit.app/?id={hu_data['ID_HU']})")
    
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
        
        st.markdown(f"**Stakeholders:** {stakeholders}")
        st.markdown(f"**Justificativas:** {justifications}")