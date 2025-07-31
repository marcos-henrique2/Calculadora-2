import streamlit as st
import matplotlib.pyplot as plt
from database import save_all_items

# --- Função de Cálculo ---
def calculate_cost(
    filament_price, weight, print_hours, power_w, energy_rate, labor_rate,
    printer_value, depr_hours, margin_pct
):
    power_kw = power_w / 1000
    errors = []
    if filament_price <= 0: errors.append("Preço do filamento deve ser > 0")
    if weight <= 0: errors.append("Filamento usado (g) deve ser > 0")
    if errors: return None, errors
    
    material_cost = (weight / 1000) * filament_price
    electricity = power_kw * print_hours * energy_rate
    labor = labor_rate * print_hours
    depreciation = (printer_value / depr_hours) * print_hours if depr_hours > 0 else 0.0
    total = material_cost + electricity + labor + depreciation
    price = total * (1 + margin_pct / 100)
    breakdown = {"Material": material_cost, "Eletricidade": electricity, "Mão de obra": labor, "Depreciação": depreciation}
    return {
        "item_name": "", "total_cost": total, "price": price, "breakdown": breakdown,
        "weight_g": weight, "print_hours": print_hours
    }, None

# --- Bloco de Segurança de Inicialização ---
if 'quote_items' not in st.session_state:
    st.session_state.quote_items = []
if 'local_calc' not in st.session_state:
    st.session_state.local_calc = None

# --- UI da Calculadora ---
st.title("🧮 Calculadora de Custo e Preço de Venda")
st.write("Preencha os dados abaixo para calcular o custo de uma peça.")
st.write("---")

st.subheader("Dados da Peça")
c1_item, c2_item = st.columns(2)
with c1_item:
    item_name = st.text_input("Nome da Peça ou Descrição")
with c2_item:
    item_material = st.text_input("Material Utilizado (Ex: PLA, ABS)", "PLA")

st.subheader("Parâmetros de Cálculo")
c1, c2 = st.columns(2)
with c1:
    filament_price = st.number_input("Preço do filamento (R$/kg)", 0.0, value=0.0, format="%.2f")
    weight = st.number_input("Filamento usado (g)", 0.0, value=0.0, format="%.2f")
    print_hours = st.number_input("Tempo de impressão (h)", 0.0, value=0.0, format="%.2f")
with c2:
    power_w = st.number_input("Potência da impressora (W)", 0.0, value=220.0, format="%.0f")
    energy_rate = st.number_input("Tarifa de energia (R$/kWh)", 0.0, value=0.90, format="%.2f")
    labor_rate = st.number_input("Valor hora da mão de obra (R$/h)", 0.0, value=0.0, format="%.2f")

printer_value = st.number_input("Valor da impressora (R$)", 0.0, value=0.0, format="%.2f")
depr_hours = st.number_input("Vida útil estimada (h)", 0.0, value=0.0, format="%.2f")
margin_pct = st.number_input("Margem de lucro (%)", 0.0, value=0.0, format="%.2f")

if st.button("Calcular (Apenas para Conferência)"):
    result, errors = calculate_cost(
        filament_price, weight, print_hours, power_w, energy_rate, labor_rate,
        printer_value, depr_hours, margin_pct
    )
    if errors:
        st.session_state.local_calc = None
        for err in errors: st.error(err)
    else:
        result['item_name'] = item_name if item_name else "Item sem nome"
        result['material_type'] = item_material
        st.session_state.local_calc = result

# --- EXIBIÇÃO DO RASCUNHO DETALHADO (BLOCO COMPLETO) ---
if st.session_state.local_calc:
    st.write("---")
    st.subheader(f"Resultado para: '{st.session_state.local_calc['item_name']}'")
    result = st.session_state.local_calc
    breakdown = result["breakdown"]
    total_cost = result["total_cost"]
    price = result["price"]
    
    # --- DETALHAMENTO DE CUSTOS RESTAURADO ---
    st.write(f"- Material: R$ {breakdown['Material']:.2f}")
    st.write(f"- Eletricidade: R$ {breakdown['Eletricidade']:.2f}")
    st.write(f"- Mão de obra: R$ {breakdown['Mão de obra']:.2f}")
    st.write(f"- Depreciação: R$ {breakdown['Depreciação']:.2f}")
    st.write(f"**Custo total:** R$ {total_cost:.2f}")
    st.write(f"**Preço sugerido:** R$ {price:.2f}")

    # --- GRÁFICO RESTAURADO ---
    fig, ax = plt.subplots()
    ax.bar(breakdown.keys(), breakdown.values(), color=["#4CAF50", "#2196F3", "#FFC107", "#9C27B0"])
    ax.set_ylabel("R$")
    st.pyplot(fig)
    st.write("---")
    
    if st.button("➕ Adicionar ao Orçamento"):
        st.session_state.quote_items.append(st.session_state.local_calc)
        save_all_items(st.session_state.quote_items)
        st.success("Item adicionado e orçamento salvo!")
        st.session_state.local_calc = None
        st.rerun()

# --- RESUMO DO ORÇAMENTO ATUAL ---
st.write("---")
st.subheader("Orçamento Atual")
if not st.session_state.quote_items:
    st.info("Nenhum item no orçamento.")
else:
    total_quote_price = sum(item['price'] for item in st.session_state.quote_items)
    st.write(f"**Itens no orçamento:** {len(st.session_state.quote_items)}")
    st.write(f"**Valor total do orçamento:** R$ {total_quote_price:.2f}")
    
    for i, item in enumerate(st.session_state.quote_items):
        col1, col2 = st.columns([0.85, 0.15])
        col1.markdown(f"- **{item['item_name']}** (R$ {item['price']:.2f})")
        if col2.button("Remover", key=f"rem_calc_{i}", use_container_width=True):
            st.session_state.quote_items.pop(i)
            save_all_items(st.session_state.quote_items)
            st.rerun()