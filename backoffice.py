import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configuração da página
st.set_page_config(page_title="Backoffice de Aprovações", layout="wide")

# Conectar ao Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(credentials)
SHEET_NAME = "Controle de HU's"
spreadsheet = client.open_by_key(st.secrets["spreadsheet"]["spreadsheet_id"])
sheet = spreadsheet.worksheet(SHEET_NAME)

# **1️⃣ Carregar os dados da planilha**
def load_hus():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df["ID_HU"] = df["ID_HU"].astype(str).str.strip()  # Garante que todos os IDs sejam strings e sem espaços
    return df

hus = load_hus()



# **3️⃣ Exibir tabela com aprovações**
st.title("📊 Painel de Aprovação de HU's")
st.dataframe(hus)

# **4️⃣ Atualizar status com base nas respostas registradas**
def atualizar_status(df):
    for index, row in df.iterrows():
        aprovacoes = str(row["Stakeholders Aprovadores"]).split(", ") if row["Stakeholders Aprovadores"] else []
        reprovacoes = str(row["Stakeholders Reprovadores"]).split(", ") if row["Stakeholders Reprovadores"] else []
        ajustes = str(row["Stakeholders Ajustes"]).split(", ") if row["Stakeholders Ajustes"] else []

        if len(aprovacoes) > 0 and len(reprovacoes) == 0 and len(ajustes) == 0:
            status = "Aprovado ✅"
        elif len(reprovacoes) > 0:
            status = "Reprovado ❌"
        elif len(ajustes) > 0:
            status = "Ajuste Necessário 🛠"
        else:
            status = "Pendente ⏳"
        
        sheet.update_cell(index + 2, 4, status)  # Atualiza a coluna de status

# Aplicar a atualização de status
atualizar_status(hus)

# **5️⃣ Exibir total de aprovações, reprovações e ajustes**
aprovados = hus[hus["Status"] == "Aprovado ✅"].shape[0]
reprovados = hus[hus["Status"] == "Reprovado ❌"].shape[0]
ajustes = hus[hus["Status"] == "Ajuste Necessário 🛠"].shape[0]
pending = hus[hus["Status"] == "Pendente ⏳"].shape[0]

st.markdown(f"**✅ Aprovados: {aprovados} | ❌ Reprovados: {reprovados} | 🛠 Ajustes: {ajustes} | ⏳ Pendentes: {pending}**")

# **6️⃣ Atualizar automaticamente ao detectar mudanças na planilha**
if st.button("🔄 Atualizar Dados"):
    st.experimental_rerun()
