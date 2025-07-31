

import streamlit as st
from database import save_all_items
from utils import create_budget_pdf

st.title("📄 Gerenciador e Exportador de Orçamento")

if 'quote_items' not in st.session_state or not st.session_state.quote_items:
    st.warning("Seu orçamento está vazio.")
    st.stop()

# --- Seção de Geração de PDF ---
with st.expander("🖨️ Gerar Orçamento em PDF para Cliente"):
    client_name = st.text_input("Nome do Cliente", "Cliente Final")
    
    if st.button("Gerar PDF", type="primary"):
        with st.spinner("Criando PDF..."):
            # A função agora só precisa do nome do cliente e dos itens
            pdf_file = create_budget_pdf(client_name, st.session_state.quote_items)
            
            st.download_button(
                label="Baixar PDF do Orçamento",
                data=pdf_file,
                file_name=f"orcamento_{client_name.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
st.write("---")

# --- Exibição da Lista de Itens (com Material) ---
st.header("Itens no Orçamento Atual")
for i, item in enumerate(st.session_state.quote_items):
    col1, col2, col3 = st.columns([4, 2, 2])
    with col1:
        st.subheader(f"{item.get('item_name', 'Item sem nome')}")
        # Mostra o material do item
        st.caption(f"Material: {item.get('material_type', 'N/A')}")
    with col2:
        st.metric(label="Preço", value=f"R$ {item.get('price', 0):.2f}")
    with col3:
        st.write("")
        if st.button("❌ Remover", key=f"remove_orc_{i}", use_container_width=True):
            st.session_state.quote_items.pop(i)
            save_all_items(st.session_state.quote_items)
            st.rerun()

st.write("---")
col_total, col_limpar = st.columns(2)
with col_total:
    total_price = sum(item.get('price', 0) for item in st.session_state.quote_items)
    st.header(f"Total: R$ {total_price:.2f}")
with col_limpar:
    st.write("")
    if st.button("🧹 Limpar Orçamento Completo", type="primary", use_container_width=True):
        st.session_state.quote_items = []
        save_all_items(st.session_state.quote_items)
        st.success("Orçamento limpo com sucesso!")
        st.rerun()