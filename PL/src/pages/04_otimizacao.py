"""
Página de Otimização - Execução de Cenários
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import json

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.services.scenario_manager import ScenarioManager
from src.services.climate_service import ClimateService
from src.models.otimizacao import run_optimization, calcular_metricas
from omegaconf import OmegaConf

st.set_page_config(page_title="Otimização", page_icon="🚀", layout="wide")

st.title("Otimização do Mix de Culturas")
st.markdown("Execute cenários e visualize os planos de plantio recomendados.")

manager = ScenarioManager()
climate = ClimateService()

if 'resultados' not in st.session_state:
    st.session_state.resultados = {}

tabs = st.tabs(["Executar", "Resultados", "Com Clima"])

# Tab 1: Executar
with tabs[0]:
    st.header("Executar Cenários")
    
    scenarios = manager.list_scenarios()
    
    selected = st.multiselect(
        "Selecione cenários para executar",
        scenarios,
        default=scenarios[:3] if len(scenarios) >= 3 else scenarios
    )
    
    if st.button("Executar Otimização", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, name in enumerate(selected):
            status_text.text(f"Executando {name}...")
            
            try:
                cfg = manager.load_scenario(name)
                cfg_dict = OmegaConf.to_container(cfg, resolve=True)
                
                resultado = run_optimization(cfg_dict, verbose=False)
                
                # Calcula métricas
                if resultado['status'] == 'Optimal':
                    metricas = calcular_metricas(resultado, cfg_dict.get('resources', {}))
                    resultado['metricas'] = metricas
                
                st.session_state.resultados[name] = resultado
                
            except Exception as e:
                st.error(f"Erro em {name}: {e}")
            
            progress_bar.progress((i + 1) / len(selected))
        
        status_text.text("Concluído!")
        st.success(f"{len(selected)} cenário(s) executado(s) com sucesso!")
        st.balloons()

# Tab 2: Resultados
with tabs[1]:
    st.header("Resultados da Otimização")
    
    if not st.session_state.resultados:
        st.warning("Nenhum resultado disponível. Execute cenários primeiro.")
    else:
        # Tabela resumo
        resumo = []
        for name, res in st.session_state.resultados.items():
            resumo.append({
                'Cenário': name,
                'Status': res['status'],
                'Lucro Total (R$)': f"R$ {res['lucro']:,.2f}" if res['lucro'] else "N/A",
                'Lucro/ha (R$)': f"R$ {res.get('metricas', {}).get('lucro_por_hectare', 0):,.2f}",
                'Área Plantada (ha)': f"{res.get('metricas', {}).get('area_total_plantada', 0):.1f}"
            })
        
        df_resumo = pd.DataFrame(resumo)
        st.dataframe(df_resumo, width='stretch')
        
        st.markdown("---")
        
        # Detalhes por cenário
        selected_detail = st.selectbox("Ver detalhes do cenário", list(st.session_state.resultados.keys()))
        
        if selected_detail:
            res = st.session_state.resultados[selected_detail]
            
            if res['status'] == 'Optimal':
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Lucro Total", f"R$ {res['lucro']:,.0f}")
                with col2:
                    area = res['metricas']['area_total_plantada']
                    st.metric("Área Total", f"{area:.1f} ha")
                with col3:
                    lucro_ha = res['metricas']['lucro_por_hectare']
                    st.metric("Lucro/ha", f"R$ {lucro_ha:,.0f}")
                with col4:
                    taxa = res['metricas']['taxa_utilizacao_area']
                    st.metric("Taxa Uso Área", f"{taxa:.1f}%")
                
                st.markdown("---")
                
                # Gráfico de plantio
                plantio = res['plantio']
                df_plantio = pd.DataFrame(list(plantio.items()), columns=['Cultura', 'Hectares'])
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    fig = px.pie(df_plantio, values='Hectares', names='Cultura', 
                                title='Distribuição do Plantio')
                    st.plotly_chart(fig, width='stretch')
                
                with col_b:
                    fig = px.bar(df_plantio, x='Cultura', y='Hectares',
                                title='Área por Cultura')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Status: {res['status']}")
                if res.get('error'):
                    st.error(f"Erro: {res['error']}")

# Tab 3: Com Clima
with tabs[2]:
    st.header("Otimização com Ajuste Climático")
    
    st.markdown("""
    Executa cenários considerando dados climáticos históricos para ajustar expectativas de produtividade.
    """)
    
    scenarios_clima = manager.list_scenarios()
    selected_clima = st.multiselect("Selecione cenários", scenarios_clima, key="sel_clima")
    
    if st.button("Executar com Clima", type="primary"):
        resultados_clima = []
        
        for name in selected_clima:
            try:
                cfg = manager.load_scenario(name)
                cfg_dict = OmegaConf.to_container(cfg, resolve=True)
                
                # Busca dados climáticos
                loc = cfg_dict.get('location', {})
                clima_res = climate.buscar_dados_clima(
                    lat=loc.get('lat', -12.5449),
                    lon=loc.get('lon', -55.7126),
                    years=loc.get('years', 2),
                    media_historica=loc.get('media_historica', 600.0)
                )
                
                # Executa otimização
                opt_res = run_optimization(cfg_dict, verbose=False)
                
                resultados_clima.append({
                    'Cenário': name,
                    'Lucro': opt_res.get('lucro'),
                    'Fator Climático': clima_res.get('fator'),
                    'Interpretação': climate.interpretar_fator_clima(clima_res.get('fator'))
                })
                
            except Exception as e:
                st.error(f"Erro em {name}: {e}")
        
        if resultados_clima:
            df_clima = pd.DataFrame(resultados_clima)
            st.dataframe(df_clima, width='stretch')
            
            fig = px.scatter(df_clima, x='Fator Climático', y='Lucro', 
                           color='Cenário', size='Lucro',
                           title='Lucro vs Fator Climático')
            st.plotly_chart(fig, width='stretch')
