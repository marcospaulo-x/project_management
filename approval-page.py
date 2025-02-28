import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def carregar_dados():
    # Autenticação com o Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("secrets.json", scope)
    client = gspread.authorize(creds)
    
    # Abrir a planilha
    sheet = client.open_by_key("1gFNF8913BXRArSLlILxdleDY5fHXq7B-S9SgiZSxNmA").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    
    st.write("📌 Dados carregados da planilha:")
    st.write(df.head())  # Exibir as primeiras linhas da planilha para depuração
    
    return df

def exibir_hu(id_hu):
    st.title("Aprovação de Histórias de Usuário")
    df = carregar_dados()
    
    st.write(f"🔎 Buscando HU: {id_hu}")  # Exibir o ID recebido
    
    # Filtrar a HU pelo ID
    hu_selecionada = df[df["ID_HU"] == id_hu]
    
    if not hu_selecionada.empty:
        st.write("🔍 HU encontrada:")
        st.write(hu_selecionada)
        link_confluence = hu_selecionada["Link"].values[0]
        st.markdown(f"[Abrir no Confluence]({link_confluence})")
    else:
        st.warning("⚠️ História de Usuário não encontrada.")

# Obter parâmetros da URL
query_params = st.experimental_get_query_params()
id_hu = query_params.get("id", [None])[0]

if id_hu:
    exibir_hu(id_hu)
else:
    st.warning("Nenhuma História de Usuário foi especificada.")
