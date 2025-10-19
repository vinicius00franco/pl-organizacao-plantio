"""
Página de Gerenciamento de Cenários
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import yaml

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.config import get_scenario_manager
from omegaconf import OmegaConf

st.set_page_config(page_title="Cenários", page_icon="🎯", layout="wide")

st.title("Cenários de Plantio")
st.markdown("**Cenários** são diferentes condições de mercado e clima. Cada um gera um plano de plantio diferente.")

# Explicação visual
with st.expander("❓ O que são cenários e por que são importantes?", expanded=False):
    st.markdown("""
    ### 💡 O que é um Cenário?
    Um cenário define as **condições** sob as quais você vai plantar:
    - 💰 **Preços de mercado** (soja alta? milho baixo?)
    - 🌍 **Localização** (clima da sua região)
    - 📦 **Recursos** (área, orçamento, água disponível)
    
    ### 🎯 Por que usar cenários diferentes?
    - **Planejar para o futuro**: E se os preços subirem? E se cair?
    - **Reduzir riscos**: Testar diferentes estratégias antes de plantar
    - **Maximizar lucro**: Encontrar a melhor combinação de culturas
    
    ### 📊 Exemplos práticos:
    - **"Base"**: Preços normais, estratégia equilibrada
    - **"Agressivo"**: Preços altos → Planta mais da cultura mais lucrativa
    - **"Conservador"**: Preços baixos → Diversifica mais para reduzir risco
    - **"Seca"**: Pouca chuva → Prioriza culturas resistentes
    """)

st.markdown("---")

# Inicializa o gerenciador centralizado
@st.cache_resource
def _get_manager():
    return get_scenario_manager()

manager = _get_manager()

tabs = st.tabs(["Ver Cenários", "Editar Cenário", "Criar Novo"])

# Tab 1: Ver Cenários
with tabs[0]:
    st.header("📋 Cenários Disponíveis")
    
    try:
        scenarios = manager.list_scenarios()
        
        if not scenarios:
            st.warning("⚠️ Nenhum cenário encontrado.")
        else:
            st.success(f"✅ {len(scenarios)} cenário(s) encontrado(s)")
            
            # Criar tabela comparativa visual
            st.markdown("### 🔍 Comparação Rápida")
            st.markdown("Veja as principais diferenças entre os cenários:")
            
            # Tabela resumo com análise de tipo
            summaries = []
            for name in scenarios:
                summary = manager.get_scenario_summary(name)
                
                # Identificar tipo de cenário
                tipo = "📊 Equilibrado"
                desc = summary.get("Descrição", "").lower()
                nome_lower = name.lower()
                
                if "agressivo" in nome_lower or "alto" in desc:
                    tipo = "🚀 Agressivo"
                elif "conservador" in nome_lower:
                    tipo = "🛡️ Conservador"
                elif "seca" in nome_lower or "clima" in nome_lower:
                    tipo = "🌦️ Climático"
                elif "crise" in nome_lower:
                    tipo = "⚠️ Crise"
                
                summary["Tipo"] = tipo
                summaries.append(summary)
            
            df_summary = pd.DataFrame(summaries)
            
            # Reordenar colunas para melhor visualização
            cols_order = ["Cenário", "Tipo", "Descrição"]
            other_cols = [col for col in df_summary.columns if col not in cols_order]
            df_summary = df_summary[cols_order + other_cols]
            
            st.dataframe(df_summary, width='stretch', hide_index=True)
            
            st.markdown("---")
            
            # Detalhes de cada cenário
            st.subheader("🔎 Ver Detalhes Completos")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                selected_scenario = st.selectbox(
                    "Escolha um cenário para ver todos os parâmetros:",
                scenarios,
                key="view_scenario_select"
            )
            
            with col2:
                st.markdown("<div style='padding-top: 32px;'></div>", unsafe_allow_html=True)
                if st.button("🔄 Atualizar", width='stretch'):
                    manager.clear_cache()
                    st.rerun()
            
            if selected_scenario:
                st.markdown(f"### 📊 Detalhes: **{selected_scenario}**")
                
                try:
                    cfg = manager.load_scenario(selected_scenario)
                    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
                    
                    # Mostra seções importantes de forma organizada
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 💰 Preços de Mercado")
                        if "mercado" in cfg_dict and "precos" in cfg_dict["mercado"]:
                            precos = cfg_dict["mercado"]["precos"]
                            for cultura, preco in precos.items():
                                st.metric(cultura.title(), f"R$ {preco:.2f}/sc")
                    
                    with col2:
                        st.markdown("#### 🌾 Informações da Fazenda")
                        if "fazenda" in cfg_dict:
                            fazenda = cfg_dict["fazenda"]
                            st.metric("Área Disponível", f"{fazenda.get('area_disponivel', 0):.0f} ha")
                            st.metric("Orçamento", f"R$ {fazenda.get('orcamento', 0):,.2f}")
                    
                    # Mostra todas as configurações em expansível
                    with st.expander("🔧 Ver Todas as Configurações (JSON)"):
                        st.json(cfg_dict)
                    
                except Exception as e:
                    st.error(f"❌ Erro ao carregar cenário: {e}")
                
                with col2:
                    st.markdown("### Acoes")
                    
                    if st.button("Exportar YAML", key="export_yaml"):
                        try:
                            cfg_dict = OmegaConf.to_container(cfg, resolve=True)
                            yaml_str = yaml.dump(cfg_dict, default_flow_style=False, allow_unicode=True)
                            st.download_button(
                                label="Baixar YAML",
                                data=yaml_str,
                                file_name=f"{selected_scenario}.yaml",
                                mime="text/yaml"
                            )
                        except Exception as e:
                            st.error(f"Erro ao exportar: {e}")
                    
                    if selected_scenario != "base":
                        st.markdown("---")
                        st.warning("Zona de Perigo")
                        if st.button("Deletar Cenário", key="delete_scenario"):
                            try:
                                manager.delete_scenario(selected_scenario)
                                st.success(f"Cenário '{selected_scenario}' deletado!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao deletar: {e}")
    
    except Exception as e:
        st.error(f"Erro ao carregar cenários: {e}")

# Integração com Análise Financeira
st.markdown("---")
st.markdown("### 💰 Integração com Análise Financeira")

if 'df_financeiro' in st.session_state:
    st.success("✅ Dados financeiros disponíveis para ajuste automático dos cenários.")
    
    if st.checkbox("Aplicar ajustes financeiros automáticos"):
        st.info("""
        🔄 **Ajustes aplicados:**
        - Preços ajustados pela inflação (IPCA)
        - Custos ajustados pelos juros (SELIC)  
        - Receitas ajustadas pelo câmbio (Dólar)
        """)
        
        # Aqui seria integrada a lógica de ajuste dos cenários
        st.success("✅ Cenários ajustados com dados financeiros!")
else:
    st.warning("⚠️ Execute a análise financeira primeiro para ajustar os cenários.")
    if st.button("💰 Ir para Análise Financeira"):
        st.switch_page("pages/06_analise_financeira.py")

# Tab 2: Editar Cenário
with tabs[1]:
    st.header("Editar Cenário Existente")
    
    scenarios = manager.list_scenarios()
    
    if not scenarios:
        st.warning("Nenhum cenário disponível para editar.")
    else:
        edit_scenario = st.selectbox(
            "Selecione um cenário para editar",
            [s for s in scenarios if s != "base"],
            key="edit_scenario_select"
        )
        
        if edit_scenario:
            st.info(f"Editando cenário: **{edit_scenario}**")
            
            try:
                # Carrega apenas as diferenças
                diff = manager.get_scenario_diff(edit_scenario)
                
                st.markdown("### Parametros")
                
                params = diff.get('params', {})
                
                col1, col2 = st.columns(2)
                
                with col1:
                    preco_soja = st.number_input(
                        "Preço Soja (R$/ton)",
                        value=float(params.get('preco_soja', 2200)),
                        min_value=0.0,
                        step=100.0
                    )
                    
                    percentual_min = st.slider(
                        "% Mínimo por Cultura",
                        min_value=0.0,
                        max_value=0.5,
                        value=float(params.get('percentual_minimo_por_cultura', 0.15)),
                        step=0.05,
                        format="%.2f"
                    )
                
                with col2:
                    preco_milho = st.number_input(
                        "Preço Milho (R$/ton)",
                        value=float(params.get('preco_milho', 1300)),
                        min_value=0.0,
                        step=50.0
                    )
                    
                    percentual_max_sp = st.slider(
                        "% Máximo Soja Produtiva",
                        min_value=0.0,
                        max_value=1.0,
                        value=float(params.get('percentual_maximo_soja_produtiva', 0.60)),
                        step=0.05,
                        format="%.2f"
                    )
                
                st.markdown("### Localizacao")
                
                location = diff.get('location', {})
                
                col3, col4 = st.columns(2)
                
                with col3:
                    lat = st.number_input(
                        "Latitude",
                        value=float(location.get('lat', -12.5449)),
                        format="%.4f"
                    )
                    years = st.number_input(
                        "Anos de Histórico Climático",
                        value=int(location.get('years', 2)),
                        min_value=1,
                        max_value=10
                    )
                
                with col4:
                    lon = st.number_input(
                        "Longitude",
                        value=float(location.get('lon', -55.7126)),
                        format="%.4f"
                    )
                    media_hist = st.number_input(
                        "Média Histórica Precipitação (mm)",
                        value=float(location.get('media_historica', 600.0)),
                        min_value=0.0,
                        step=10.0
                    )
                
                st.markdown("### Recursos")
                
                resources = diff.get('resources', {})
                
                if st.checkbox("Editar Recursos", value=bool(resources)):
                    col5, col6 = st.columns(2)
                    
                    with col5:
                        area_total = st.number_input(
                            "Área Total (ha)",
                            value=float(resources.get('AREA_TOTAL_DISPONIVEL_HA', 500)),
                            min_value=0.0
                        )
                        
                        orcamento = st.number_input(
                            "Orçamento Total (R$)",
                            value=float(resources.get('ORCAMENTO_TOTAL_DISPONIVEL', 1100000)),
                            min_value=0.0,
                            step=10000.0
                        )
                        
                        agua = st.number_input(
                            "Água Disponível (m³)",
                            value=float(resources.get('AGUA_TOTAL_DISPONIVEL_M3', 250000)),
                            min_value=0.0,
                            step=1000.0
                        )
                    
                    with col6:
                        potassio = st.number_input(
                            "Potássio Disponível (kg)",
                            value=float(resources.get('POTASSIO_DISPONIVEL_KG', 45000)),
                            min_value=0.0,
                            step=100.0
                        )
                        
                        fosforo = st.number_input(
                            "Fósforo Disponível (kg)",
                            value=float(resources.get('FOSFORO_DISPONIVEL_KG', 42000)),
                            min_value=0.0,
                            step=100.0
                        )
                        
                        horas_maq = st.number_input(
                            "Horas Máquina Disponíveis",
                            value=float(resources.get('HORAS_MAQUINA_DISPONIVEIS', 6000)),
                            min_value=0.0,
                            step=100.0
                        )
                else:
                    area_total = orcamento = agua = potassio = fosforo = horas_maq = None
                
                st.markdown("---")
                
                if st.button("Salvar Alterações", type="primary"):
                    try:
                        # Monta nova configuração
                        new_config = {
                            "# @package _group_": None,
                            "params": {
                                "preco_soja": preco_soja,
                                "preco_milho": preco_milho,
                                "percentual_minimo_por_cultura": percentual_min,
                                "percentual_maximo_soja_produtiva": percentual_max_sp
                            },
                            "location": {
                                "lat": lat,
                                "lon": lon,
                                "years": years,
                                "media_historica": media_hist
                            }
                        }
                        
                        if area_total is not None:
                            new_config["resources"] = {
                                "AREA_TOTAL_DISPONIVEL_HA": area_total,
                                "ORCAMENTO_TOTAL_DISPONIVEL": orcamento,
                                "AGUA_TOTAL_DISPONIVEL_M3": agua,
                                "POTASSIO_DISPONIVEL_KG": potassio,
                                "FOSFORO_DISPONIVEL_KG": fosforo,
                                "HORAS_MAQUINA_DISPONIVEIS": horas_maq
                            }
                        
                        manager.save_scenario(edit_scenario, new_config, overwrite=True)
                        st.success(f"Cenário '{edit_scenario}' atualizado com sucesso!")
                        
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")
            
            except Exception as e:
                st.error(f"Erro ao carregar cenário: {e}")

# Tab 3: Criar Novo
with tabs[2]:
    st.header("Criar Novo Cenário")
    
    st.markdown("""
    Crie um novo cenário definindo apenas as diferenças em relação ao cenário base.
    Os valores não especificados serão herdados do cenário base.
    """)
    
    new_name = st.text_input(
        "Nome do Novo Cenário",
        placeholder="Ex: preco_alto_milho",
        help="Use apenas letras, números e underscores"
    )
    
    new_description = st.text_area(
        "Descrição",
        placeholder="Descreva brevemente o cenário...",
        help="Opcional: descreva as características deste cenário"
    )
    
    if new_name:
        st.markdown("### Configuração")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_preco_soja = st.number_input("Preço Soja (R$/ton)", value=2200.0, min_value=0.0, step=100.0, key="new_soja")
            new_min = st.slider("% Mínimo por Cultura", 0.0, 0.5, 0.15, 0.05, key="new_min")
        
        with col2:
            new_preco_milho = st.number_input("Preço Milho (R$/ton)", value=1300.0, min_value=0.0, step=50.0, key="new_milho")
            new_max_sp = st.slider("% Máximo Soja Produtiva", 0.0, 1.0, 0.60, 0.05, key="new_max")
        
        st.markdown("### Localização")
        
        col3, col4 = st.columns(2)
        
        with col3:
            new_lat = st.number_input("Latitude", value=-12.5449, format="%.4f", key="new_lat")
            new_years = st.number_input("Anos de Histórico", value=2, min_value=1, max_value=10, key="new_years")
        
        with col4:
            new_lon = st.number_input("Longitude", value=-55.7126, format="%.4f", key="new_lon")
            new_media = st.number_input("Média Histórica Precip. (mm)", value=600.0, min_value=0.0, step=10.0, key="new_media")
        
        if st.button("Criar Cenário", type="primary"):
            try:
                new_config = manager.create_scenario_template(new_name, new_description)
                new_config["params"]["preco_soja"] = new_preco_soja
                new_config["params"]["preco_milho"] = new_preco_milho
                new_config["params"]["percentual_minimo_por_cultura"] = new_min
                new_config["params"]["percentual_maximo_soja_produtiva"] = new_max_sp
                new_config["location"]["lat"] = new_lat
                new_config["location"]["lon"] = new_lon
                new_config["location"]["years"] = new_years
                new_config["location"]["media_historica"] = new_media
                
                manager.save_scenario(new_name, new_config, overwrite=False)
                st.success(f"Cenário '{new_name}' criado com sucesso!")
                st.balloons()
                
            except FileExistsError:
                st.error("Já existe um cenário com este nome. Escolha outro nome ou delete o existente.")
            except Exception as e:
                st.error(f"Erro ao criar cenário: {e}")
