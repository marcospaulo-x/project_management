import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# Definir o escopo de acesso ao Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Carregar credenciais do Streamlit Cloud (do secrets.toml)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    {
        "type": "service_account",
        "project_id": st.secrets["gcp"]["project_id"],
        "private_key_id": st.secrets["gcp"]["private_key_id"],
        "private_key": st.secrets["gcp"]["private_key"],
        "client_email": st.secrets["gcp"]["client_email"],
        "client_id": st.secrets["gcp"]["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": st.secrets["gcp"]["client_x509_cert_url"]
    },
    scope
)

# Autenticação com o Google Sheets
gc = gspread.authorize(credentials)

# Abrir a planilha
try:
    planilha = gc.open("Gerenciamento de aprovações de HU's").sheet1
    dados = planilha.get_all_records()
    df = pd.DataFrame(dados)
    
    if df.empty:
        st.warning("⚠️ A planilha está vazia. Adicione dados antes de continuar.")
    else:
        st.write("### Lista de HUs para aprovação")
        
        # Verifica se as colunas esperadas existem
        colunas_esperadas = ["ID", "Título"]
        colunas_faltando = [col for col in colunas_esperadas if col not in df.columns]

        if colunas_faltando:
            st.error(f"🚨 As colunas {colunas_faltando} não foram encontradas na planilha.")
            st.write("Colunas disponíveis na planilha:", df.columns.tolist())
        else:
            for _, row in df.iterrows():
                st.write(f"**ID:** {row['ID']} - **{row['Título']}**")
                st.write(f"[Ver detalhes](approval-page?page={row['ID']})")  # Link para a página de aprovação
                st.write("---")

except gspread.exceptions.SpreadsheetNotFound:
    st.error("🚨 A planilha não foi encontrada. Verifique se o nome está correto.")
except Exception as e:
    st.error(f"🚨 Erro inesperado: {e}")
