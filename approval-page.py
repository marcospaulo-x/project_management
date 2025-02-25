import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Configurações do Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(credentials)
SHEET_NAME = "Controle de HU's"
spreadsheet = client.open_by_key(st.secrets["spreadsheet"]["spreadsheet_id"])
sheet = spreadsheet.worksheet(SHEET_NAME)

# Obter ID da HU da URL
hu_id = st.query_params.get("id", [None])[0]

if hu_id:
    # Buscar informações da HU na planilha
    records = sheet.get_all_records()
    hu_data = next((row for row in records if row["ID_HU"] == hu_id), None)
    
    if hu_data:
        st.title("Aprovação de Histórias de Usuário")
        st.subheader(f"{hu_data['ID_HU']} - {hu_data['Título']}")

        # Exibir botões de ação
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Aprovar"):
                action = "Aprovado"
        with col2:
            if st.button("Reprovar"):
                action = "Reprovado"
        with col3:
            if st.button("Ajustar"):
                action = "Ajuste"
        
        if "action" in locals():
            stakeholder_name = st.text_input("Digite seu nome:")
            observacao = st.text_area("Adicione uma observação (opcional):")
            if st.button("Confirmar ação"):
                row_idx = next(i for i, row in enumerate(records, start=2) if row["ID_HU"] == hu_id)
                sheet.update(f"C{row_idx}", action)  # Atualiza Status
                sheet.update(f"D{row_idx}", stakeholder_name)  # Atualiza Stakeholder Aprovador
                sheet.update(f"E{row_idx}", observacao)  # Atualiza Observação
                st.success("Ação registrada com sucesso!")
                st.rerun()

        # Exibir iframe com o link do Confluence
        st.markdown(f"""
            <iframe src="{hu_data['Link']}" width="100%" height="600px"></iframe>
        """, unsafe_allow_html=True)
    else:
        st.error("História de Usuário não encontrada.")
else:
    st.error("ID da HU não especificado.")
