import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Backoffice de Aprovação de HUs", layout="centered")

# Conectar ao Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(credentials)
SHEET_NAME = "Controle de HU's"
spreadsheet = client.open_by_key(st.secrets["spreadsheet"]["spreadsheet_id"])
sheet = spreadsheet.worksheet(SHEET_NAME)

# Função para carregar dados
@st.cache_data(ttl=300)
def load_hus():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df["ID_HU"] = df["ID_HU"].astype(str).str.strip()
    return df

# Funções auxiliares
def get_majority_status(hus, hu_id):
    hu_votes = hus[hus["ID_HU"] == hu_id]
    if hu_votes.empty:
        return "Pendente"
    status_counts = hu_votes["Status"].value_counts()
    return status_counts.idxmax()

def get_vote_counts(hus, hu_id):
    hu_votes = hus[hus["ID_HU"] == hu_id]
    approved_count = hu_votes[hu_votes["Status"] == "Aprovado"].shape[0]
    rejected_count = hu_votes[hu_votes["Status"] == "Reprovado"].shape[0]
    adjustment_count = hu_votes[hu_votes["Status"] == "Ajuste Solicitado"].shape[0]
    return approved_count, rejected_count, adjustment_count

def get_stakeholders_and_justifications(hus, hu_id):
    hu_votes = hus[hus["ID_HU"] == hu_id]
    stakeholders = hu_votes[["Stakeholder Aprovador", "Status", "Observação"]].dropna(subset=["Stakeholder Aprovador"])
    return stakeholders

# Função para obter o emoji correto com base no status
def get_status_emoji(status):
    if status == "Aprovado":
        return "✅"
    elif status == "Reprovado":
        return "❌"
    elif status == "Ajuste Solicitado":
        return "🔧"
    return None  # Retorna None para status desconhecido

# Título
st.title("Cadastro e Gerenciamento de Histórias de Usuários")

# Recarregar os dados da planilha
hus = load_hus()  # Carrega os dados antes de usar a variável "hus"

# Formulário para adicionar nova HU
st.subheader("Adicionar Nova HU")
with st.form(key="new_hu_form"):
    new_id = st.text_input("ID da HU:")
    new_title = st.text_input("Título da HU:")
    new_project = st.text_input("Projeto:")
    new_link = st.text_input("Link do Confluence:")
    submit_button = st.form_submit_button("Cadastrar HU")
    
    if submit_button:
        if not new_id or not new_title or not new_link or not new_project:
            st.error("⚠️ Todos os campos são obrigatórios!")
        elif new_id in hus["ID_HU"].values:
            st.error("⚠️ ID da HU já existe. Escolha um ID único.")
        else:
            approval_link = f"https://aprovacao-de-hus.streamlit.app/?id={new_id}"
            creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Data e hora atuais
            responsible = "Marcos Paulo"  # Responsável fixo
            sheet.append_row([new_project, new_id, new_title, "Pendente", "", "", new_link, approval_link, creation_date, responsible])
            st.success(f"{new_id} cadastrada com sucesso!")
            st.cache_data.clear()  # Limpa o cache para recarregar os dados
            hus = load_hus()  # Recarrega os dados da planilha
            selected_hu = new_id  # Seleciona automaticamente a HU cadastrada

# Dropdown para selecionar a HU
hu_list = [""] + hus["ID_HU"].drop_duplicates().tolist()  # Lista de HUs disponíveis
default_index = 0  # Índice padrão (primeiro item, que é vazio)

# Verifica se a HU cadastrada está na lista e define o índice correspondente
if "selected_hu" in locals() and selected_hu in hu_list:
    default_index = hu_list.index(selected_hu)

selected_hu = st.selectbox("Selecione uma História de Usuário:", hu_list, index=default_index)

# Exibir detalhes da HU selecionada
if selected_hu and selected_hu != "":
    hus = load_hus()
    hu_data = hus[hus["ID_HU"] == selected_hu]
    
    if not hu_data.empty:
        hu_data = hu_data.iloc[0]  # Obtém a primeira linha correspondente
        
        status = get_majority_status(hus, selected_hu)
        approved_count, rejected_count, adjustment_count = get_vote_counts(hus, selected_hu)
        stakeholders = get_stakeholders_and_justifications(hus, selected_hu)
        
        status_colors = {
            "Aprovado": "#28a745",
            "Reprovado": "#dc3545",
            "Ajuste Solicitado": "#ffc107",
            "Pendente": "#6c757d"
        }
        status_color = status_colors.get(status, "#6c757d")

        # Layout em grid com cards
        col1, col2 = st.columns(2)  # Duas colunas para os cards superiores

        with col1:
            # Card de Detalhes da HU
            st.markdown(
                f"""
                <div style='background-color:#2e2e2e; padding:14px; border-radius:10px; border: 1px solid #444; color: white;'>
                    <p style='font-size:18px; font-weight:bold;'>📄 Detalhes da HU</p>
                    <p style='font-size:16px;'>📂 <strong>Projeto:</strong> {hu_data.get('Projeto', 'Não informado')}</p>
                    <p style='font-size:16px;'>🔗 <strong>Link Confluence:</strong> <a href="{hu_data['Link']}" target="_blank" style='color: #1e90ff;'>Acessar</a></p>
                    <p style='font-size:16px;'>📝 <strong>Link para Aprovação:</strong> <a href="https://aprovacao-de-hus.streamlit.app/?id={hu_data['ID_HU']}" target="_blank" style='color: #1e90ff;'>Aprovar</a></p>
                    <p style='font-size:16px;'>👤 <strong>Responsável:</strong> {hu_data.get('Responsável', 'Marcos Paulo')}</p>
                    <p style='font-size:16px;'>📅 <strong>Data de Criação:</strong> {hu_data.get('Data de Criação', 'Não informada')}</p>                          
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            # Card de Status e Votos
            st.markdown(
                f"""
                <div style='background-color:#2e2e2e; padding:13px; border-radius:10px; border: 1px solid #444; color: white;'>
                    <p style='font-size:18px; font-weight:bold;'>📊 Status e Votos</p>
                    <div style='padding:15px; border-radius:10px; text-align:center; 
                                font-size:22px; font-weight:bold; background-color:{status_color}; color:white;'>
                        {status}
                    </div>
                    <br>
                    <div style='display:flex; justify-content:space-between;'>
                        <div style='text-align:center;'>
                            <p style='font-size:16px;'>✔️ Aprovados</p>
                            <p style='font-size:24px; font-weight:bold;'>{approved_count}</p>
                        </div>
                        <div style='text-align:center;'>
                            <p style='font-size:16px;'>❌ Reprovados</p>
                            <p style='font-size:24px; font-weight:bold;'>{rejected_count}</p>
                        </div>
                        <div style='text-align:center;'>
                            <p style='font-size:16px;'>🔧 Ajustes Solicitados</p>
                            <p style='font-size:24px; font-weight:bold;'>{adjustment_count}</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        
        # Adiciona espaçamento antes da seção
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        # Seção de Stakeholders e Justificativas
        if not stakeholders.empty:  # Exibe a seção apenas se houver stakeholders
            with st.expander("🔍 Ver Decisão por Stakeholder", expanded=False):
                for _, row in stakeholders.iterrows():
                    emoji = get_status_emoji(row['Status'])
                    if emoji:  # Exibe o card apenas se houver um emoji válido
                        st.markdown(f"**{emoji} {row['Stakeholder Aprovador']}** - {row['Status']}")
                        if pd.notna(row["Observação"]):
                            st.write(f"📝 {row['Observação']}")
    else:
        st.error("⚠️ História de Usuário não encontrada.")