import streamlit as st
from database import save_all_items

# --- Funções de Conversão ---
def to_float(value_str):
    try:
        return float(str(value_str).replace(',', '.'))
    except (ValueError, AttributeError):
        return 0.0

def parse_time_to_decimal(time_str):
    try:
        time_str = str(time_str).replace(',', '.')
        if '.' in time_str:
            parts = time_str.split('.')
            hours = int(parts[0]) if parts[0] else 0
            minutes_str = parts[1] if len(parts) > 1 and parts[1] else '0'
            minutes = int(minutes_str)
            return hours + (minutes / 60.0)
        else:
            return float(time_str)
    except (ValueError, AttributeError):
        return 0.0

# --- Função de Cálculo ---
def calculate_cost(
    filament_price, weight, print_hours, power_w, energy_rate,
    labor_rate, active_work_hours,
    printer_value, depr_hours, margin_pct, 
    maintenance_cost_per_hour, failure_rate_pct, post_processing_cost, complexity_multiplier
):
    power_kw = power_w / 1000
    errors = []
    if filament_price <= 0 and weight > 0: errors.append("Preço do filamento deve ser > 0")
    if weight <= 0: errors.append("Filamento usado (g) deve ser > 0")
    if errors: return None, errors
    
    labor_cost = labor_rate * active_work_hours
    material_cost = (weight / 1000) * filament_price
    electricity_cost = power_kw * print_hours * energy_rate
    depreciation_cost = (printer_value / depr_hours) * print_hours if depr_hours > 0 else 0.0
    material_adjusted_cost = material_cost * (1 + (failure_rate_pct / 100))
    maintenance_total_cost = maintenance_cost_per_hour * print_hours
    
    production_cost = (
        material_adjusted_cost + electricity_cost + labor_cost + 
        depreciation_cost + maintenance_total_cost + post_processing_cost
    )
    
    cost_with_complexity = production_cost * complexity_multiplier
    price = cost_with_complexity * (1 + (margin_pct / 100))
    cost_per_hour = production_cost / print_hours if print_hours > 0 else 0
    
    breakdown = {
        "Material (c/ falha)": material_adjusted_cost, "Eletricidade": electricity_cost, 
        "Mão de obra": labor_cost, "Depreciação": depreciation_cost,
        "Manutenção": maintenance_total_cost, "Pós-Processamento": post_processing_cost
    }
    
    return {
        "item_name": "", "total_cost": production_cost, "price": price, "breakdown": breakdown,
        "weight_g": weight, "print_hours": print_hours, "cost_per_hour": cost_per_hour
    }, None

# --- Bloco de Segurança de Inicialização ---
if 'quote_items' not in st.session_state:
    st.session_state.quote_items = []
if 'local_calc' not in st.session_state:
    st.session_state.local_calc = None

# --- UI da Calculadora ---
st.title("🧮 Calculadora de Custo e Preço de Venda")
st.info("Nos campos de tempo, use vírgula para separar horas e minutos (ex: 2,30 para 2h 30min).")
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

st.subheader("Parâmetros da Máquina e Impressão")
c1, c2 = st.columns(2)
with c1:
    filament_price_str = st.text_input("Preço do filamento (R$/kg)", value="100,00")
    weight_str = st.text_input("Filamento usado (g)", value="50,00")
    print_hours_str = st.text_input("Tempo de impressão (h)", value="10,30")
with c2:
    power_w_str = st.text_input("Potência da impressora (W)", value="220")
    energy_rate_str = st.text_input("Tarifa de energia (R$/kWh)", value="0,70")
    printer_value_str = st.text_input("Valor da impressora (R$)", value="1500,00")
    depr_hours_str = st.text_input("Vida útil estimada (h)", value="5000,0")

st.subheader("Seu Trabalho e Estratégia")
c3, c4 = st.columns(2)
with c3:
    labor_rate_str = st.text_input("Valor da sua hora de trabalho (R$/h)", value="40,00")
    active_work_hours_str = st.text_input("Tempo de Trabalho Ativo (h)", value="0,30", help="Tempo gasto preparando o arquivo, a impressora, removendo suportes, limpando a peça, etc.")
    post_processing_cost_str = st.text_input("Custo Adicional de Acabamento (R$)", value="0,00")
with c4:
    maintenance_cost_str = st.text_input("Custo de Manutenção (R$/h)", value="0,05")
    failure_rate_str = st.text_input("Taxa de Falha (%)", value="10,0")
    complexity_options = {"Simples (1.0x)": 1.0, "Moderado (1.25x)": 1.25, "Complexo (1.5x)": 1.5, "Extremo (2.0x)": 2.0}
    complexity_label = st.selectbox("Complexidade da Peça", options=list(complexity_options.keys()))
    margin_pct_str = st.text_input("Margem de lucro (%)", value="100,0")

if st.button("Calcular (Apenas para Conferência)"):
    # Conversão de todos os valores
    filament_price = to_float(filament_price_str)
    weight = to_float(weight_str)
    print_hours = parse_time_to_decimal(print_hours_str)
    power_w = to_float(power_w_str)
    energy_rate = to_float(energy_rate_str)
    labor_rate = to_float(labor_rate_str)
    active_work_hours = parse_time_to_decimal(active_work_hours_str)
    printer_value = to_float(printer_value_str)
    depr_hours = to_float(depr_hours_str)
    margin_pct = to_float(margin_pct_str)
    maintenance_cost_per_hour = to_float(maintenance_cost_str)
    failure_rate_pct = to_float(failure_rate_str)
    post_processing_cost = to_float(post_processing_cost_str)
    complexity_multiplier = complexity_options[complexity_label]

    result, errors = calculate_cost(
        filament_price, weight, print_hours, power_w, energy_rate,
        labor_rate, active_work_hours,
        printer_value, depr_hours, margin_pct,
        maintenance_cost_per_hour, failure_rate_pct, post_processing_cost, complexity_multiplier
    )
    if errors:
        st.session_state.local_calc = None
        for err in errors: st.error(err)
    else:
        result['item_name'] = item_name if item_name else "Item sem nome"
        result['material_type'] = item_material
        result['quantity'] = item_quantity
        result['painting'] = item_painting
        # CORREÇÃO DO BUG: Garantimos que o preço final é calculado e salvo corretamente.
        result['final_price'] = result['price'] * result.get('quantity', 1)
        st.session_state.local_calc = result

# --- Exibição do Rascunho Detalhado ---
if st.session_state.local_calc:
    st.write("---")
    st.subheader(f"Resultado para: '{st.session_state.local_calc['item_name']}'")
    result = st.session_state.local_calc
    breakdown = result["breakdown"]
    total_cost = result["total_cost"]
    price = result["price"]
    
    st.write(f"**Preço sugerido de Venda (un.): R$ {price:.2f}**")
    # CORREÇÃO DO BUG: Exibimos o preço total corretamente.
    st.write(f"**Preço Total ({result.get('quantity', 1)} un.): R$ {result.get('final_price', 0):.2f}**")
    st.write("---")

    with st.expander("Ver composição detalhada dos custos"):
        if breakdown['Material (c/ falha)'] > 0: st.write(f"- Material (c/ ajuste de falha): R$ {breakdown['Material (c/ falha)']:.2f}")
        if breakdown['Eletricidade'] > 0: st.write(f"- Eletricidade: R$ {breakdown['Eletricidade']:.2f}")
        if breakdown['Mão de obra'] > 0: st.write(f"- Mão de obra: R$ {breakdown['Mão de obra']:.2f}")
        if breakdown['Depreciação'] > 0: st.write(f"- Depreciação: R$ {breakdown['Depreciação']:.2f}")
        if breakdown['Manutenção'] > 0: st.write(f"- Manutenção: R$ {breakdown['Manutenção']:.2f}")
        if breakdown['Pós-Processamento'] > 0: st.write(f"- Pós-Processamento: R$ {breakdown['Pós-Processamento']:.2f}")
        st.write("---")
        st.write(f"**Custo total de Produção (un.): R$ {total_cost:.2f}**")

    if st.button("➕ Adicionar ao Orçamento"):
        st.session_state.quote_items.append(st.session_state.local_calc)
        #save_all_items(st.session_state.quote_items) <- Removido para simplificar
        st.success("Item adicionado ao orçamento da sessão!")
        st.rerun()

# --- Resumo do Orçamento Atual ---
if st.session_state.quote_items:
    st.write("---")
    st.subheader("Orçamento Atual")
    total_quote_price = sum(item['final_price'] for item in st.session_state.quote_items)
    st.write(f"**Valor total do orçamento:** R$ {total_quote_price:.2f}")
    
    for i, item in enumerate(st.session_state.quote_items):
        col1, col2 = st.columns([0.85, 0.15])
        col1.markdown(f"- ({item['quantity']}x) **{item['item_name']}** (R$ {item['final_price']:.2f})")
        if col2.button("Remover", key=f"rem_calc_{i}", use_container_width=True):
            st.session_state.quote_items.pop(i)
            #save_all_items(st.session_state.quote_items) <- Removido para simplificar
            st.rerun()