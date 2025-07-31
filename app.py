import streamlit as st
from database import init_db, load_items

# Inicializa o DB e carrega os dados para a sessão
init_db()
if 'quote_items' not in st.session_state:
    st.session_state.quote_items = load_items()
if 'local_calc' not in st.session_state:
    st.session_state.local_calc = None

st.set_page_config(
    page_title="Home | Calculadora 3D Print",
    layout="wide"
)

# A navegação é criada AUTOMATICAMENTE pelo Streamlit por causa da pasta 'pages'.
st.sidebar.success("Selecione uma página acima.")

st.title("Bem-vindo à Calculadora 3D Print!")
st.markdown("Use o menu na barra lateral para navegar entre as páginas.")