import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Aprovação de Histórias de Usuário", layout="centered")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(credentials)
SHEET_NAME = "Controle de HU's"
spreadsheet = client.open_by_key(st.secrets["spreadsheet"]["spreadsheet_id"])
sheet = spreadsheet.worksheet(SHEET_NAME)

@st.cache_data
def load_hus():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df["ID_HU"] = df["ID_HU"].astype(str).str.strip()
    return df

hus = load_hus()
hu_id = st.query_params.get("id", [""])[0].strip()
hu_data = hus[hus["ID_HU"] == hu_id]

if not hu_data.empty:
    hu = hu_data.iloc[0]
    st.title(f"📝 Aprovação da HU - {hu['Título']}")
    st.markdown(f"[🔗 Link para o Confluence]({hu['Link']})")
    st.markdown(f'<iframe src="{hu["Link"]}" width="100%" height="800"></iframe>', unsafe_allow_html=True)

    # Botões de Aprovação com colunas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("Aprovar")
    with col2:
        st.button("Reprovar")
    with col3:
        st.button("Ajustar")
    
    # Formulário de Aprovação
    if st.button("Mostrar Formulário"):
        with st.form("form_aprovacao"):
            nome = st.text_input("Seu Nome")
            observacao = st.text_area("Observação (opcional)")
            submit = st.form_submit_button("Confirmar")

            if submit:
                if not nome:
                    st.error("⚠️ Nome é obrigatório para registrar a aprovação!")
                else:
                    # Lógica para atualizar a planilha...
                    st.success("✅ Resposta registrada com sucesso!")
else:
    st.error("⚠️ História de Usuário não encontrada.")