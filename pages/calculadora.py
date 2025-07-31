import streamlit as st
from database import save_all_items

# --- Função de Conversão ---
def to_float(value_str):
    """Converte uma string (com ponto ou vírgula) para um número float."""
    try:
        return float(str(value_str).replace(',', '.'))
    except (ValueError, AttributeError):
        return 0.0

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
    total_cost = material_cost + electricity + labor + depreciation
    price = total_cost * (1 + margin_pct / 100)
    cost_per_hour = total_cost / print_hours if print_hours > 0 else 0
    breakdown = {"Material": material_cost, "Eletricidade": electricity, "Mão de obra": labor, "Depreciação": depreciation}
    return {
        "item_name": "", "total_cost": total_cost, "price": price, "breakdown": breakdown,
        "weight_g": weight, "print_hours": print_hours, "cost_per_hour": cost_per_hour
    }, None

# --- Bloco de Segurança de Inicialização ---
if 'quote_items' not in st.session_state:
    st.session_state.quote_items = []
if 'local_calc' not in st.session_state:
    st.session_state.local_calc = None

# --- UI da Calculadora ---
st.title("🧮 Calculadora de Custo e Preço de Venda")
st.info("Agora você pode usar vírgula (,) para os valores decimais.")
st.write("---")

st.subheader("Dados da Peça")
col1_item, col2_item, col3_item = st.columns([3, 2, 1])
with col1_item:
    item_name = st.text_input("Nome da Peça ou Descrição")
with col2_item:
    item_material = st.text_input("Material Utilizado (Ex: PLA, ABS)", "PLA")
with col3_item:
    item_quantity = st.number_input("Quantidade", min_value=1, value=1, step=1)

item_painting = st.selectbox("Pintura Manual?", ["Não", "Sim"])

st.subheader("Parâmetros de Cálculo (para 1 unidade)")
c1, c2 = st.columns(2)
with c1:
    filament_price_str = st.text_input("Preço do filamento (R$/kg)", value="0,00")
    weight_str = st.text_input("Filamento usado (g)", value="0,00")
    print_hours_str = st.text_input("Tempo de impressão (h)", value="0,0")
with c2:
    power_w_str = st.text_input("Potência da impressora (W)", value="220")
    energy_rate_str = st.text_input("Tarifa de energia (R$/kWh)", value="0,70")
    labor_rate_str = st.text_input("Valor hora da mão de obra (R$/h)", value="0,00")

printer_value_str = st.text_input("Valor da impressora (R$)", value="0,00")
depr_hours_str = st.text_input("Vida útil estimada (h)", value="0,0")
margin_pct_str = st.text_input("Margem de lucro (%)", value="0,0")

if st.button("Calcular (Apenas para Conferência)"):
    # --- CONVERSÃO DOS VALORES ---
    filament_price = to_float(filament_price_str)
    weight = to_float(weight_str)
    print_hours = to_float(print_hours_str)
    power_w = to_float(power_w_str)
    energy_rate = to_float(energy_rate_str)
    labor_rate = to_float(labor_rate_str)
    printer_value = to_float(printer_value_str)
    depr_hours = to_float(depr_hours_str)
    margin_pct = to_float(margin_pct_str)

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
        result['quantity'] = item_quantity
        result['painting'] = item_painting
        result['final_price'] = result['price'] * item_quantity
        st.session_state.local_calc = result

# --- Exibição do Rascunho Detalhado ---
if st.session_state.local_calc:
    st.write("---")
    st.subheader(f"Resultado para: '{st.session_state.local_calc['item_name']}'")
    result = st.session_state.local_calc
    breakdown = result["breakdown"]
    total_cost = result["total_cost"]
    price = result["price"]
    
    # --- LÓGICA DE EXIBIÇÃO CORRIGIDA ---
    # Cada linha só aparece se o valor for maior que zero.
    if breakdown['Material'] > 0:
        st.write(f"- **Valor gasto em filamento (un.): R$ {breakdown['Material']:.2f}**")
    if result['cost_per_hour'] > 0:
        st.write(f"- **Custo por Hora (R$/h): R$ {result['cost_per_hour']:.2f}**")
    st.write("---")
    if breakdown['Eletricidade'] > 0:
        st.write(f"- Custo Eletricidade (un.): R$ {breakdown['Eletricidade']:.2f}")
    if breakdown['Mão de obra'] > 0:
        st.write(f"- Custo Mão de obra (un.): R$ {breakdown['Mão de obra']:.2f}")
    if breakdown['Depreciação'] > 0:
        st.write(f"- Custo Depreciação (un.): R$ {breakdown['Depreciação']:.2f}")
    
    st.write(f"**Custo total (un.):** R$ {total_cost:.2f}")
    st.write(f"**Preço sugerido (un.):** R$ {price:.2f}")
    st.write(f"**Preço Total ({result['quantity']} un.):** R$ {result['final_price']:.2f}")
    st.write("---")
    
    if st.button("➕ Adicionar ao Orçamento"):
        st.session_state.quote_items.append(st.session_state.local_calc)
        save_all_items(st.session_state.quote_items)
        st.success("Item adicionado e orçamento salvo!")
        st.rerun()

# --- Resumo do Orçamento Atual ---
st.write("---")
st.subheader("Orçamento Atual")
if not st.session_state.quote_items:
    st.info("Nenhum item no orçamento.")
else:
    total_quote_price = sum(item['final_price'] for item in st.session_state.quote_items)
    st.write(f"**Itens no orçamento:** {len(st.session_state.quote_items)}")
    st.write(f"**Valor total do orçamento:** R$ {total_quote_price:.2f}")
    
    for i, item in enumerate(st.session_state.quote_items):
        col1, col2 = st.columns([0.85, 0.15])
        col1.markdown(f"- ({item['quantity']}x) **{item['item_name']}** (R$ {item['final_price']:.2f})")
        if col2.button("Remover", key=f"rem_calc_{i}", use_container_width=True):
            st.session_state.quote_items.pop(i)
            save_all_items(st.session_state.quote_items)
            st.rerun()