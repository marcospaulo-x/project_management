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
    st.markdown(f"[🔗 Link para o Confluence]({hu['Link']})")

    # Exibir iframe com o Confluence (ajustado para ocupar mais espaço)
    st.markdown(
        f'<iframe src="{hu["Link"]}" width="100%" height="600" style="border: 1px solid #ddd; border-radius: 10px; margin-bottom: 20px;"></iframe>',
        unsafe_allow_html=True
    )

    # **Botões de Aprovação**
    st.write("### Decisão de Aprovação")

    # Estilos CSS para os botões personalizados
    st.markdown(
        """
        <style>
        .custom-button {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            color: white;
            margin: 5px;
            width: 100%;
        }
        .custom-button:hover {
            opacity: 0.8;
        }
        .custom-button.selected {
            border: 2px solid #000;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
        }
        #aprovar {
            background-color: #4CAF50;
        }
        #reprovar {
            background-color: #F44336;
        }
        #ajustar {
            background-color: #FFC107;
            color: black;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Usar colunas para posicionar os botões lado a lado
    col1, col2, col3 = st.columns(3)
    with col1:
        aprovar = st.markdown(
            '<div class="custom-button" id="aprovar" onclick="handleButtonClick(\'Aprovar\')">Aprovar</div>',
            unsafe_allow_html=True
        )
    with col2:
        reprovar = st.markdown(
            '<div class="custom-button" id="reprovar" onclick="handleButtonClick(\'Reprovar\')">Reprovar</div>',
            unsafe_allow_html=True
        )
    with col3:
        ajustar = st.markdown(
            '<div class="custom-button" id="ajustar" onclick="handleButtonClick(\'Ajustar\')">Ajustar</div>',
            unsafe_allow_html=True
        )

    # JavaScript para lidar com o clique nos botões
    st.markdown(
        """
        <script>
        function handleButtonClick(decisao) {
            // Remove a classe 'selected' de todos os botões
            document.querySelectorAll('.custom-button').forEach(button => {
                button.classList.remove('selected');
            });

            // Adiciona a classe 'selected' ao botão clicado
            event.target.classList.add('selected');

            // Envia a decisão para o Streamlit
            fetch('/_stcore/streamlit_component', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ decisao: decisao }),
            });
        }
        </script>
        """,
        unsafe_allow_html=True
    )

    # Exibir formulário somente se uma decisão foi selecionada
    if "decisao" in st.session_state:
        with st.form("form_aprovacao"):
            st.write(f"Você selecionou: **{st.session_state.decisao}**")
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

else:
    st.error("⚠️ História de Usuário não encontrada.")