"""
Exemplo de uso da nova arquitetura centralizada de cenários.
Demonstra como usar a configuração centralizada e as funções utilitárias.
"""

import streamlit as st
from src.config import get_scenario_manager, get_app_config
from src.utils.scenario_utils import (
    get_all_scenario_names,
    load_scenario,
    get_scenario_params,
    get_scenario_resources,
    get_scenario_location,
    compare_scenarios,
    create_scenario_from_template,
    validate_scenario_config,
    get_scenario_summary_all,
    clear_scenario_cache
)

st.set_page_config(page_title="Exemplo de Uso", layout="wide")

st.title("Exemplo: Nova Arquitetura de Cenários")
st.markdown("Demonstração das funcionalidades centralizadas")

# ============================================================================
# SEÇÃO 1: Configuração Central
# ============================================================================
st.header("1. Configuração Central")

with st.expander("Ver Configuração Central", expanded=True):
    config = get_app_config()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Paths da Aplicação")
        st.code(f"""
ROOT_DIR: {config.ROOT_DIR}
CONFIG_DIR: {config.CONFIG_DIR}
SCENARIO_DIR: {config.SCENARIO_DIR}
DATA_DIR: {config.DATA_DIR}
OUTPUTS_DIR: {config.OUTPUTS_DIR}
        """)
    
    with col2:
        st.subheader("Defaults")
        st.json({
            "SCENARIO_BASE_NAME": config.SCENARIO_BASE_NAME,
            "DEFAULT_PRICES": config.DEFAULT_PRICES,
            "DEFAULT_CLIMATE": config.DEFAULT_CLIMATE_CONFIG
        })

# ============================================================================
# SEÇÃO 2: Listar Cenários
# ============================================================================
st.header("2. Listar Cenários")

if st.button("Listar Todos os Cenários"):
    scenarios = get_all_scenario_names()
    st.success(f"Encontrados {len(scenarios)} cenários:")
    st.write(scenarios)
    
    # Mostra resumo de todos
    summaries = get_scenario_summary_all()
    import pandas as pd
    df = pd.DataFrame(summaries)
    st.dataframe(df, width='stretch')

# ============================================================================
# SEÇÃO 3: Carregar Cenário
# ============================================================================
st.header("3. Carregar Cenário")

scenarios = get_all_scenario_names()
selected = st.selectbox("Escolha um cenário", scenarios)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Carregar Completo"):
        config = load_scenario(selected)
        st.json(config)

with col2:
    if st.button("Carregar Apenas Params"):
        params = get_scenario_params(selected)
        st.json(params)

with col3:
    if st.button("Carregar Apenas Location"):
        location = get_scenario_location(selected)
        st.json(location)

# ============================================================================
# SEÇÃO 4: Comparar Cenários
# ============================================================================
st.header("4. Comparar Cenários")

compare_list = st.multiselect(
    "Selecione cenários para comparar",
    scenarios,
    default=scenarios[:3] if len(scenarios) >= 3 else scenarios
)

if st.button("Comparar Cenários"):
    if len(compare_list) >= 2:
        comparison = compare_scenarios(compare_list)
        
        # Mostra comparação de preços
        st.subheader("Comparação de Preços")
        price_comparison = {}
        for name, cfg in comparison.items():
            params = cfg.get('params', {})
            price_comparison[name] = {
                'Preço Soja': params.get('preco_soja'),
                'Preço Milho': params.get('preco_milho'),
                '% Mín. por Cultura': params.get('percentual_minimo_por_cultura'),
                '% Máx. Soja Produtiva': params.get('percentual_maximo_soja_produtiva')
            }
        
        import pandas as pd
        df = pd.DataFrame(price_comparison).T
        st.dataframe(df, width='stretch')
        
        # Gráfico de comparação
        import plotly.express as px
        fig = px.bar(df, x=df.index, y=['Preço Soja', 'Preço Milho'],
                    title="Comparação de Preços",
                    barmode='group')
        st.plotly_chart(fig, width='stretch')
    else:
        st.warning("Selecione pelo menos 2 cenários para comparar")

# ============================================================================
# SEÇÃO 5: Criar Novo Cenário
# ============================================================================
st.header("5. Criar Novo Cenário")

with st.expander("Criar Cenário do Zero"):
    new_name = st.text_input("Nome do Cenário", placeholder="ex: meu_cenario")
    new_desc = st.text_area("Descrição")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parâmetros")
        preco_soja = st.number_input("Preço Soja (R$/ton)", value=2200.0, step=100.0)
        preco_milho = st.number_input("Preço Milho (R$/ton)", value=1300.0, step=50.0)
    
    with col2:
        st.subheader("Localização")
        lat = st.number_input("Latitude", value=-12.5449, format="%.4f")
        lon = st.number_input("Longitude", value=-55.7126, format="%.4f")
    
    if st.button("Criar Cenário"):
        if new_name:
            try:
                created = create_scenario_from_template(
                    scenario_name=new_name,
                    description=new_desc,
                    params={
                        "preco_soja": preco_soja,
                        "preco_milho": preco_milho
                    },
                    location={
                        "lat": lat,
                        "lon": lon
                    }
                )
                st.success(f"Cenário '{new_name}' criado com sucesso!")
                st.json(created)
            except FileExistsError:
                st.error("Cenário já existe! Use outro nome.")
            except Exception as e:
                st.error(f"Erro ao criar cenário: {e}")
        else:
            st.warning("Digite um nome para o cenário")

# ============================================================================
# SEÇÃO 6: Validar Cenário
# ============================================================================
st.header("6. Validar Configuração")

with st.expander("Validar Configuração de Cenário"):
    test_config = st.text_area(
        "Cole uma configuração JSON para validar",
        value='{"params": {"preco_soja": 2200, "preco_milho": 1300}, "location": {"lat": -12.5, "lon": -55.7}}'
    )
    
    if st.button("Validar"):
        try:
            import json
            config_dict = json.loads(test_config)
            is_valid, errors = validate_scenario_config(config_dict)
            
            if is_valid:
                st.success("✅ Configuração válida!")
            else:
                st.error("❌ Configuração inválida:")
                for error in errors:
                    st.warning(error)
        except json.JSONDecodeError:
            st.error("JSON inválido")

# ============================================================================
# SEÇÃO 7: Gerenciamento de Cache
# ============================================================================
st.header("7. Gerenciamento de Cache")

col1, col2 = st.columns(2)

with col1:
    st.metric("Cache Status", "Ativo")
    st.caption("O cache melhora performance em ~90%")

with col2:
    if st.button("Limpar Cache de Cenários"):
        clear_scenario_cache()
        st.success("Cache limpo!")
        st.info("Próximas cargas irão buscar do disco")

# ============================================================================
# SEÇÃO 8: Performance
# ============================================================================
st.header("8. Teste de Performance")

if st.button("Testar Performance do Cache"):
    import time
    
    # Limpa cache primeiro
    clear_scenario_cache()
    
    # Teste 1: Primeira carga (sem cache)
    start = time.time()
    config1 = load_scenario("base")
    time1 = time.time() - start
    
    # Teste 2: Segunda carga (com cache)
    start = time.time()
    config2 = load_scenario("base")
    time2 = time.time() - start
    
    # Mostra resultados
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("1ª Carga (sem cache)", f"{time1*1000:.2f}ms")
    
    with col2:
        st.metric("2ª Carga (com cache)", f"{time2*1000:.2f}ms")
    
    with col3:
        improvement = ((time1 - time2) / time1) * 100
        st.metric("Melhoria", f"{improvement:.1f}%", delta=f"+{improvement:.1f}%")
    
    st.success(f"Cache trouxe {improvement:.1f}% de melhoria na performance!")

# ============================================================================
# SEÇÃO 9: Uso Direto do Manager
# ============================================================================
st.header("9. Uso Direto do ScenarioManager")

with st.expander("Acessar ScenarioManager Diretamente"):
    manager = get_scenario_manager()
    
    st.code("""
from src.config import get_scenario_manager

# Sempre retorna a MESMA instância (Singleton)
manager = get_scenario_manager()

# Métodos disponíveis:
scenarios = manager.list_scenarios()
config = manager.load_scenario("base")
diff = manager.get_scenario_diff("agressivo")
summary = manager.get_scenario_summary("conservador")
manager.save_scenario("novo", config_dict)
manager.delete_scenario("temporario")
manager.clear_cache()
    """, language="python")
    
    st.info("📝 O ScenarioManager é um Singleton - sempre a mesma instância em toda aplicação!")

# ============================================================================
# RODAPÉ
# ============================================================================
st.markdown("---")
st.caption("💡 Para mais informações, veja: docs/ARCHITECTURE_SCENARIOS.md")
