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
query_params = st.query_params
hu_id = query_params.get("id", [""])  # Captura o primeiro valor da lista
hu_id = str(hu_id).strip()  # Converte para string e remove espaços

# **2️⃣ Carregar os dados da planilha**
@st.cache_data
def load_hus():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df["ID_HU"] = df["ID_HU"].astype(str).str.strip()  # Garante que todos os IDs sejam strings
    return df

hus = load_hus()

# **3️⃣ Buscar a HU correspondente**
hu_data = hus[hus["ID_HU"] == hu_id]  # Filtra a HU correspondente

if not hu_data.empty:
    hu = hu_data.iloc[0]  # Obtém a primeira linha correspondente

    # **Exibir informações**
    st.title(f"📝 Aprovação da HU - {hu['Título']}")

    # Botão discreto para o link do Confluence
    st.markdown(
        """
        <style>
        .confluence-button {
            background-color: transparent;
            color: #2E86C1;
            padding: 8px 16px;
            border: 1px solid #2E86C1;
            border-radius: 5px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
            margin: 10px 0;
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        .confluence-button:hover {
            background-color: #2E86C1;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        f'<a href="{hu["Link"]}" target="_blank" class="confluence-button">Link para o Confluence</a>',
        unsafe_allow_html=True
    )

    # Exibir iframe com o Confluence (ajustado para ocupar mais espaço)
    st.markdown(
        f'<iframe src="{hu["Link"]}" width="100%" height="800" style="border: 1px solid #ddd; border-radius: 10px;"></iframe>',
        unsafe_allow_html=True
    )

    # **Botões de Aprovação**
    st.write("### Decisão de Aprovação")

    # CSS personalizado para modificar a cor do texto exibido
    st.markdown(
        """
        <style>
        .green-text {
            color: #4CAF50 !important; /* Verde */
        }
        .red-text {
            color: #F44336 !important; /* Vermelho */
        }
        .yellow-text {
            color: #FFC107 !important; /* Amarelo */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Usar colunas para posicionar os botões lado a lado
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Aprovar ✅", key="aprovar", use_container_width=True):
            st.session_state.decisao = "Aprovar"
    with col2:
        if st.button("Reprovar ❌", key="reprovar", use_container_width=True):
            st.session_state.decisao = "Reprovar"
    with col3:
        if st.button("Ajustar 🛠", key="ajustar", use_container_width=True):
            st.session_state.decisao = "Ajustar"

    # Exibir formulário somente se uma decisão foi selecionada
    if "decisao" in st.session_state:
        with st.form("form_aprovacao"):
            # Exibir a decisão selecionada com a palavra colorida
            if st.session_state.decisao == "Aprovar":
                st.markdown(
                    'Você selecionou: <strong class="green-text">Aprovar</strong>',
                    unsafe_allow_html=True
                )
            elif st.session_state.decisao == "Reprovar":
                st.markdown(
                    'Você selecionou: <strong class="red-text">Reprovar</strong>',
                    unsafe_allow_html=True
                )
            elif st.session_state.decisao == "Ajustar":
                st.markdown(
                    'Você selecionou: <strong class="yellow-text">Ajustar</strong>',
                    unsafe_allow_html=True
                )

            nome = st.text_input("Seu Nome", placeholder="Digite seu nome")
            observacao = st.text_area("Observação (opcional)", placeholder="Digite uma observação, se necessário")
            submit = st.form_submit_button("Confirmar")

            if submit:
                if not nome:
                    st.error("⚠️ Nome é obrigatório para registrar a aprovação!")
                else:
                    # Atualizar a planilha com a decisão
                    row_index = hu_data.index[0] + 2  # Linha da HU na planilha (gspread começa em 1)
                    sheet.update_cell(row_index, 3, st.session_state.decisao)  # Atualiza 'Status'
                    sheet.update_cell(row_index, 4, nome)  # Atualiza 'Stakeholder Aprovador'
                    sheet.update_cell(row_index, 5, observacao)  # Atualiza 'Observação'

                    st.success("✅ Resposta registrada com sucesso!")
                    del st.session_state.decisao  # Limpa a decisão após o envio

    # Adicionar imagem no rodapé
    st.markdown(
        """
        <style>
        .footer {
            text-align: center;
            margin-top: 40px;
        }
        </style>
        <div class="footer">
            <a href="https://ibb.co/pjF6n89K"><img src="https://i.ibb.co/nMJqRv51/rodap-pagina-de-aprova-o.png" alt="rodap-pagina-de-aprova-o" border="0"></a><br /><a target='_blank' href='https://pt-br.imgbb.com/'>como colocar foto no email</a><br />
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    st.error("⚠️ História de Usuário não encontrada.")