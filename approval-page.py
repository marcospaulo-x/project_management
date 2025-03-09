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
hu_id = st.query_params.get("id")  # Captura o valor do parâmetro "id"

if hu_id:
    hu_id = hu_id.strip()  # Remove espaços em branco
    
    # **2️⃣ Carregar os dados da planilha**
    def load_hus():
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        df["ID_HU"] = df["ID_HU"].astype(str).str.strip()  # Garante que todos os IDs sejam strings e sem espaços
        return df

    hus = load_hus()

    # **3️⃣ Buscar a HU correspondente**
    hu_data = hus[hus["ID_HU"] == hu_id]

    if not hu_data.empty:
        hu = hu_data.iloc[0]  # Obtém a primeira linha correspondente

        # **Exibir informações**
        st.title(f"📝 Aprovação da HU - {hu['Título']}")
        st.markdown(f"[🔗 Link para o Confluence]({hu['Link']})")

        # **Botões de Aprovação**
        st.write("### Decisão de Aprovação")

        # CSS personalizado para modificar a cor do texto exibido
        st.markdown(
            """
            <style>
            .green-text { color: #4CAF50 !important; } /* Verde */
            .red-text { color: #F44336 !important; } /* Vermelho */
            .yellow-text { color: #FFC107 !important; } /* Amarelo */
            </style>
            """,
            unsafe_allow_html=True
        )

        # Usar colunas para posicionar os botões lado a lado
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Aprovar ✅", key="aprovar", use_container_width=True):
                st.session_state.decisao = "Aprovado"
        with col2:
            if st.button("Reprovar ❌", key="reprovar", use_container_width=True):
                st.session_state.decisao = "Reprovado"
        with col3:
            if st.button("Ajustar 🛠", key="ajustar", use_container_width=True):
                st.session_state.decisao = "Ajuste Solicitado"

        # Exibir formulário somente se uma decisão foi selecionada
        if "decisao" in st.session_state:
            with st.form("form_aprovacao"):
                # Exibir a decisão selecionada com a palavra colorida
                if st.session_state.decisao == "Aprovado":
                    st.markdown('Você selecionou: <strong class="green-text">Aprovar</strong>', unsafe_allow_html=True)
                elif st.session_state.decisao == "Reprovado":
                    st.markdown('Você selecionou: <strong class="red-text">Reprovar</strong>', unsafe_allow_html=True)
                elif st.session_state.decisao == "Ajuste Solicitado":
                    st.markdown('Você selecionou: <strong class="yellow-text">Ajustar</strong>', unsafe_allow_html=True)

                nome = st.text_input("Seu Nome", placeholder="Digite seu nome")
                observacao = st.text_area("Observação (opcional)", placeholder="Digite uma observação, se necessário")
                submit = st.form_submit_button("Confirmar")

                if submit:
                    if not nome:
                        st.error("⚠️ Nome é obrigatório para registrar a aprovação!")
                    else:
                        # Adiciona uma nova linha com o voto do stakeholder
                        sheet.append_row([hu["Projeto"], hu["ID_HU"], hu["Título"], st.session_state.decisao, nome, observacao, hu["Link"], hu["Link Aprovação"]])
                        st.success("✅ Resposta registrada com sucesso!")
                        del st.session_state.decisao  # Limpa a decisão após o envio

        # Exibir iframe com o Confluence
        st.markdown(
            f'<iframe src="{hu["Link"]}" width="100%" height="800" style="border: 1px solid #ddd; border-radius: 10px;"></iframe>',
            unsafe_allow_html=True
        )

    else:
        st.error("⚠️ História de Usuário não encontrada.")
else:
    st.error("⚠️ ID da HU não encontrado na URL.")