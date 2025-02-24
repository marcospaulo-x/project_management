import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# Autenticação com Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("secrets.json", scope)
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
