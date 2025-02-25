import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configuração da página
st.set_page_config(page_title="Aprovação de Histórias de Usuário", layout="centered")

# Conectar ao Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(credentials)
SHEET_NAME = "Controle de HU's"
spreadsheet = client.open_by_key(st.secrets["spreadsheet"]["spreadsheet_id"])
sheet = spreadsheet.worksheet(SHEET_NAME)

# **1️⃣ Capturar o ID da HU da URL**
query_params = st.query_params  # Substitui experimental_get_query_params
hu_id = query_params.get("id", [""])[0].strip()  # Remove espaços desnecessários

# **Debug: Exibir o ID capturado**
st.write(f"ID capturado: {hu_id}")

# **2️⃣ Carregar os dados da planilha**
@st.cache_data
def load_hus():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df["ID_HU"] = df["ID_HU"].astype(str).str.strip()  # Garante que todos os IDs sejam strings
    return df

hus = load_hus()

# **Debug: Exibir a lista de IDs disponíveis na planilha**
st.write("IDs disponíveis na planilha:", hus["ID_HU"].tolist())

# **3️⃣ Buscar a HU correspondente**
hu_data = hus[hus["ID_HU"] == hu_id]  # Agora deve funcionar corretamente

if not hu_data.empty:
    hu = hu_data.iloc[0]  # Obtém a primeira linha correspondente

    # **Exibir informações**
    st.title(f"📝 Aprovação da HU - {hu['Título']}")
    st.markdown(f"[🔗 Link para o Confluence]({hu['Link']})")

    # Exibir iframe com o Confluence (se permitido)
    st.markdown(
        f'<iframe src="{hu["Link"]}" width="100%" height="500"></iframe>',
        unsafe_allow_html=True
    )

    # **Botões de Aprovação**
    with st.form("form_aprovacao"):
        aprovacao = st.radio("Decisão:", ["Aprovar", "Reprovar", "Ajustar"])
        nome = st.text_input("Seu Nome")
        observacao = st.text_area("Observação (opcional)")
        submit = st.form_submit_button("Confirmar")

        if submit:
            if not nome:
                st.error("⚠️ Nome é obrigatório para registrar a aprovação!")
            else:
                # Atualizar a planilha com a decisão
                row_index = hu_data.index[0] + 2  # Linha da HU na planilha (gspread começa em 1)
                sheet.update_cell(row_index, 3, aprovacao)  # Atualiza 'Status'
                sheet.update_cell(row_index, 4, nome)  # Atualiza 'Stakeholder Aprovador'
                sheet.update_cell(row_index, 5, observacao)  # Atualiza 'Observação'

                st.success("✅ Resposta registrada com sucesso!")

else:
    st.error("⚠️ História de Usuário não encontrada.")
