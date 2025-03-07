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

    # **Correção na contagem dos votos**
    approved_count = hus[hus["ID_HU"] == selected_hu]["Aprovado"].sum()
    rejected_count = hus[hus["ID_HU"] == selected_hu]["Reprovado"].sum()
    adjustment_count = hus[hus["ID_HU"] == selected_hu]["Ajuste Solicitado"].sum()

    # **Atualiza o status com base nos votos**
    if approved_count > max(rejected_count, adjustment_count):
        new_status = "Aprovado"
    elif rejected_count > max(approved_count, adjustment_count):
        new_status = "Reprovado"
    elif adjustment_count > max(approved_count, rejected_count):
        new_status = "Ajuste Solicitado"
    else:
        new_status = "Pendente"
    
    # **Verifica se o status precisa ser atualizado na planilha**
    if new_status != status:
        hu_index = hus.index[hus["ID_HU"] == selected_hu].tolist()[0] + 2  # Índice no Google Sheets
        sheet.update_cell(hu_index, 4, new_status)
        status = new_status
    
    # **Layout melhorado com colunas**
    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader(hu_data['Título'])
        st.markdown(f"📂 **Projeto:** {hu_data.get('Projeto', 'Não informado')}")
        st.markdown(f"🔗 [Link Confluence]({hu_data['Link']})")
        st.markdown(f"📝 [Link para Aprovação](https://aprovacao-de-hus.streamlit.app/?id={hu_data['ID_HU']})")

    with col2:
        st.markdown("### 📌 Status Atual")
        st.markdown(
            f"<div style='background-color:{status_color}; color:white; padding:10px; border-radius:10px; text-align:center; font-size:18px; font-weight:bold;'>{status}</div>",
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.metric("✔️ Aprovados", approved_count)
        st.metric("❌ Reprovados", rejected_count)
        st.metric("🔧 Ajustes Solicitados", adjustment_count)
