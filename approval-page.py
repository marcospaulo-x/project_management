import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.title("Aprovação de Histórias de Usuário")

# Configuração do Google Sheets
scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
gc = gspread.authorize(credentials)
planilha = gc.open("Gerenciamento de aprovações de HU's").sheet1

# Obter o ID da HU na URL
hu_id = st.query_params.get("page", [""])[0]

if hu_id:
    dados = planilha.get_all_records()
    hu = next((row for row in dados if str(row["ID"]) == hu_id), None)
    
    if hu:
        # Exibir ID e Título
        st.subheader(f"HU{hu['ID']} - {hu['Título']}")

        # Criar botões lado a lado
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Aprovar"):
                planilha.update_cell(planilha.find(str(hu["ID"])).row, 3, "Aprovado")
                st.success("HU aprovada com sucesso!")
        with col2:
            if st.button("❌ Reprovar"):
                planilha.update_cell(planilha.find(str(hu["ID"])).row, 3, "Reprovado")
                st.error("HU reprovada!")
        with col3:
            if st.button("🛠 Ajustar"):
                planilha.update_cell(planilha.find(str(hu["ID"])).row, 3, "Ajuste necessário")
                st.warning("HU marcada para ajuste!")

        # Exibir a página do link dentro da própria página (iframe)
        if "Link" in hu and hu["Link"]:
            st.write("🔗 **Detalhes da HU:**")
            st.markdown(f'<iframe src="{hu["Link"]}" width="100%" height="600px"></iframe>', unsafe_allow_html=True)
        else:
            st.warning("Nenhum link disponível para esta HU.")
    
    else:
        st.error("História de Usuário não encontrada.")
else:
    st.error("Nenhuma HU especificada.")
