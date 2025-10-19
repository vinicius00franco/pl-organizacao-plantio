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

from src.config import get_scenario_manager
from src.services.climate_service import ClimateService
from src.models.otimizacao import run_optimization, calcular_metricas, calcular_recursos_utilizados
from src.utils.scenario_utils import get_scenario_params
from omegaconf import OmegaConf

st.set_page_config(page_title="Otimização", page_icon="🚀", layout="wide")

st.title("Plano de Plantio Otimizado")
st.markdown("**Como funciona:** Escolha cenários → Execute otimização → Veja seu plano de plantio ideal")

manager = get_scenario_manager()
climate = ClimateService()

if 'resultados' not in st.session_state:
    st.session_state.resultados = {}

# Explicação visual no topo
with st.expander("Como os cenários afetam o plano de plantio?", expanded=False):
    st.markdown("""
    ### O que é um cenário?
    Um cenário define as **condições do seu negócio**:
    - 💰 **Preços** de venda (soja, milho, etc.)
    - 📍 **Localização** da fazenda (clima)
    - 📦 **Recursos** disponíveis (área, orçamento, água)
    
    ### Como funciona a otimização?
    1. Você escolhe um **cenário** (ex: "agressivo" com preços altos)
    2. O sistema calcula qual **mix de culturas** maximiza seu lucro
    3. Você vê um **plano de plantio** visual e detalhado
    
    ### Exemplo prático:
    - **Cenário "conservador"**: Preços baixos → Planta mais culturas de menor risco
    - **Cenário "agressivo"**: Preços altos → Planta mais soja para maximizar lucro
    """)

st.markdown("---")

tabs = st.tabs(["🎯 Escolher e Executar", "📊 Ver Plano de Plantio", "🌤️ Com Clima"])

# Tab 1: Escolher e Executar - MELHORADO
with tabs[0]:
    st.header("1. Escolha seus Cenários")
    
    scenarios = manager.list_scenarios()
    
    # Mostra informações dos cenários ANTES de selecionar
    st.markdown("### Cenários Disponíveis:")
    
    scenario_info = []
    for name in scenarios:
        params = get_scenario_params(name)
        scenario_info.append({
            'Cenário': name,
            'Preço Soja': f"R$ {params.get('preco_soja', 0):,.0f}",
            'Preço Milho': f"R$ {params.get('preco_milho', 0):,.0f}",
            'Estratégia': '🎯 Alto risco/retorno' if params.get('preco_soja', 0) > 2300 else '🛡️ Conservadora'
        })
    
    df_info = pd.DataFrame(scenario_info)
    st.dataframe(df_info, width='stretch', hide_index=True)
    
    st.markdown("---")
    st.markdown("### 2. Selecione Cenários para Comparar")
    
    selected = st.multiselect(
        "Escolha até 3 cenários para comparar",
        scenarios,
        default=[scenarios[0]] if scenarios else [],
        max_selections=3,
        help="Selecione diferentes cenários para ver como os preços afetam o plano de plantio"
    )
    
    if not selected:
        st.info("👆 Selecione pelo menos um cenário acima para começar")
    else:
        st.success(f"✅ {len(selected)} cenário(s) selecionado(s): {', '.join(selected)}")
        
        # Mostra comparação de parâmetros dos selecionados
        with st.expander("Ver detalhes dos cenários selecionados"):
            comparacao = []
            for name in selected:
                params = get_scenario_params(name)
                comparacao.append({
                    'Cenário': name,
                    'Preço Soja (R$/ton)': params.get('preco_soja', 0),
                    'Preço Milho (R$/ton)': params.get('preco_milho', 0),
                    '% Mínimo/Cultura': f"{params.get('percentual_minimo_por_cultura', 0)*100:.0f}%",
                    '% Máx. Soja Produtiva': f"{params.get('percentual_maximo_soja_produtiva', 0)*100:.0f}%"
                })
            df_comp = pd.DataFrame(comparacao)
            st.dataframe(df_comp, width='stretch', hide_index=True)
        
        st.markdown("---")
        st.markdown("### 3. Execute a Otimização")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Calcular Plano de Plantio Ótimo", type="primary", width='stretch'):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, name in enumerate(selected):
                    status_text.text(f"Calculando plano para cenário: {name}...")
                    
                    try:
                        cfg = manager.load_scenario(name)
                        cfg_dict = OmegaConf.to_container(cfg, resolve=True)
                        
                        resultado = run_optimization(cfg_dict, verbose=False)
                        
                        # Calcula métricas
                        if resultado['status'] == 'Optimal':
                            metricas = calcular_metricas(resultado, cfg_dict.get('resources', {}))
                            # NOVO: Calcular recursos utilizados
                            params_df = pd.DataFrame(resultado.get('params_agregados', {}))
                            recursos_analise = calcular_recursos_utilizados(
                                resultado, 
                                cfg_dict.get('resources', {}), 
                                params_df
                            )
                            resultado['recursos_analise'] = recursos_analise
                            resultado['metricas'] = metricas
                            # Adiciona parâmetros para referência
                            resultado['params'] = cfg_dict.get('params', {})
                        
                        st.session_state.resultados[name] = resultado
                        
                    except Exception as e:
                        st.error(f"Erro ao calcular {name}: {e}")
                    
                    progress_bar.progress((i + 1) / len(selected))
                
                status_text.empty()
                progress_bar.empty()
                st.success("✅ Planos calculados! Veja a aba 'Ver Plano de Plantio'")
                st.balloons()
                st.info("👉 Clique na aba **'Ver Plano de Plantio'** acima para ver os resultados")

# Tab 2: Ver Plano - COMPLETAMENTE REDESENHADO
with tabs[1]:
    st.header("Seu Plano de Plantio Otimizado")
    
    if not st.session_state.resultados:
        st.info("""
        ### 📝 Como usar:
        1. Vá para a aba **"Escolher e Executar"**
        2. Selecione os cenários que deseja comparar
        3. Clique em **"Calcular Plano de Plantio"**
        4. Volte aqui para ver os resultados
        """)
    else:
        # Comparação lado a lado
        if len(st.session_state.resultados) > 1:
            st.markdown("### 📊 Comparação entre Cenários")
            
            # Resumo comparativo
            dados_comp = []
            for name, res in st.session_state.resultados.items():
                if res['status'] == 'Optimal':
                    dados_comp.append({
                        'Cenário': name,
                        'Lucro Total': res['lucro'],
                        'Lucro/ha': res.get('metricas', {}).get('lucro_por_hectare', 0),
                        'Área Usada (ha)': res.get('metricas', {}).get('area_total_plantada', 0)
                    })
            
            if dados_comp:
                df_comp = pd.DataFrame(dados_comp)
                
                # Gráficos lado a lado: Barras + Linha
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gráfico de barras comparativo
                    fig = px.bar(df_comp, x='Cenário', y='Lucro Total',
                                title='💰 Lucro Total por Cenário',
                                color='Lucro Total',
                                color_continuous_scale='Greens',
                                text='Lucro Total')
                    fig.update_traces(texttemplate='R$ %{text:,.0f}', textposition='outside')
                    fig.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig, width='stretch')
                
                with col2:
                    # NOVO: Gráfico de linha conectando os lucros
                    fig_linha = px.line(
                        df_comp,
                        x='Cenário',
                        y='Lucro Total',
                        title='📈 Comparação de Lucros - Visão Linear',
                        markers=True,
                        line_shape='linear'
                    )
                    fig_linha.update_traces(
                        mode='lines+markers+text',
                        text=df_comp['Cenário'],
                        textposition='top center',
                        hovertemplate='<b>%{text}</b><br>Lucro: R$ %{y:,.0f}<extra></extra>'
                    )
                    fig_linha.update_layout(
                        xaxis_title="Cenários",
                        yaxis_title="Lucro Total (R$)",
                        showlegend=False
                    )
                    # Adicionar valores sobre os pontos
                    for i, row in df_comp.iterrows():
                        fig_linha.add_annotation(
                            x=row['Cenário'],
                            y=row['Lucro Total'],
                            text=f"R$ {row['Lucro Total']:,.0f}",
                            showarrow=False,
                            yshift=10,
                            font=dict(size=10, color='black')
                        )
                    st.plotly_chart(fig_linha, width='stretch')
                
                # Destaque para melhor cenário
                melhor = df_comp.loc[df_comp['Lucro Total'].idxmax()]
                st.success(f"🏆 **Melhor cenário:** {melhor['Cenário']} com lucro de R$ {melhor['Lucro Total']:,.2f}")
                
                # Tabela comparativa
                st.markdown("#### 📋 Comparação Detalhada")
                df_comp_exibir = df_comp.copy()
                df_comp_exibir['Lucro Total'] = df_comp_exibir['Lucro Total'].apply(lambda x: f"R$ {x:,.0f}")
                df_comp_exibir['Lucro/ha'] = df_comp_exibir['Lucro/ha'].apply(lambda x: f"R$ {x:,.0f}")
                df_comp_exibir['Área Usada (ha)'] = df_comp_exibir['Área Usada (ha)'].apply(lambda x: f"{x:.1f}")
                st.dataframe(df_comp_exibir, width='stretch', hide_index=True)
        
        st.markdown("---")
        st.markdown("### 🌾 Detalhes do Plano de Plantio")
        
        # Seletor de cenário
        selected_detail = st.selectbox(
            "Escolha um cenário para ver o plano detalhado:",
            list(st.session_state.resultados.keys()),
            key="detail_select"
        )
        
        if selected_detail:
            res = st.session_state.resultados[selected_detail]
            
            if res['status'] == 'Optimal':
                # Mostra parâmetros do cenário
                with st.expander(f"⚙️ Parâmetros do cenário '{selected_detail}'", expanded=False):
                    params = res.get('params', {})
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Preço Soja", f"R$ {params.get('preco_soja', 0):,.0f}/ton")
                    with col2:
                        st.metric("Preço Milho", f"R$ {params.get('preco_milho', 0):,.0f}/ton")
                    with col3:
                        st.metric("% Mín/Cultura", f"{params.get('percentual_minimo_por_cultura', 0)*100:.0f}%")
                    with col4:
                        st.metric("% Máx Soja", f"{params.get('percentual_maximo_soja_produtiva', 0)*100:.0f}%")
                
                # Métricas principais - VISUAL MELHORADO
                st.markdown("#### 💡 Resumo Financeiro")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    lucro = res['lucro']
                    st.metric("💰 Lucro Total", f"R$ {lucro:,.0f}")
                with col2:
                    area = res['metricas']['area_total_plantada']
                    st.metric("📏 Área Plantada", f"{area:.1f} ha")
                with col3:
                    lucro_ha = res['metricas']['lucro_por_hectare']
                    st.metric("📈 Lucro por Hectare", f"R$ {lucro_ha:,.0f}/ha")
                with col4:
                    taxa = res['metricas']['taxa_utilizacao_area']
                    st.metric("📊 Taxa de Uso", f"{taxa:.1f}%")
                
                st.markdown("---")
                
                # NOVO: Análise de Recursos Não Utilizados
                st.markdown("#### 📊 Análise de Recursos")
                
                if 'recursos_analise' in res and res['recursos_analise']:
                    recursos = res['recursos_analise']
                    
                    # Mapeamento de nomes amigáveis para os recursos
                    nomes_recursos = {
                        'AREA_TOTAL_DISPONIVEL_HA': {'nome': 'Área Total Disponível', 'unidade': 'ha', 'icone': '🌾'},
                        'AREA_NAO_COMPACTADA_HA': {'nome': 'Área Não Compactada', 'unidade': 'ha', 'icone': '🌱'},
                        'ORCAMENTO_TOTAL_DISPONIVEL': {'nome': 'Orçamento Total', 'unidade': 'R$', 'icone': '💰'},
                        'AGUA_TOTAL_DISPONIVEL_M3': {'nome': 'Água Disponível', 'unidade': 'm³', 'icone': '💧'},
                        'POTASSIO_DISPONIVEL_KG': {'nome': 'Potássio Disponível', 'unidade': 'kg', 'icone': '🧪'},
                        'FOSFORO_DISPONIVEL_KG': {'nome': 'Fósforo Disponível', 'unidade': 'kg', 'icone': '🧫'},
                        'HORAS_MAQUINA_DISPONIVEIS': {'nome': 'Horas de Máquina', 'unidade': 'h', 'icone': '🚜'},
                        'CAPACIDADE_SILO_TON': {'nome': 'Capacidade do Silo', 'unidade': 'ton', 'icone': '🏭'}
                    }
                    
                    # Criar DataFrame para visualização
                    dados_recursos = []
                    for recurso_key, analise in recursos.items():
                        if recurso_key in nomes_recursos:
                            info = nomes_recursos[recurso_key]
                            dados_recursos.append({
                                'Recurso': f"{info['icone']} {info['nome']}",
                                'Disponível': analise['disponivel'],
                                'Utilizado': analise['utilizado'],
                                'Não Utilizado': analise['nao_utilizado'],
                                'Utilização': analise['percentual_utilizado'],
                                'Unidade': info['unidade']
                            })
                    
                    df_recursos = pd.DataFrame(dados_recursos)
                    
                    # Gráfico de barras empilhadas para visualização
                    fig_recursos = px.bar(
                        df_recursos,
                        x='Recurso',
                        y=['Utilizado', 'Não Utilizado'],
                        title='📊 Utilização de Recursos - Disponível vs Utilizado',
                        barmode='stack',
                        color_discrete_map={'Utilizado': 'green', 'Não Utilizado': 'lightgray'},
                        text_auto='.1f'
                    )
                    fig_recursos.update_layout(
                        xaxis_title="Recursos",
                        yaxis_title="Quantidade",
                        showlegend=True
                    )
                    st.plotly_chart(fig_recursos, width='stretch')
                    
                    # Tabela detalhada
                    st.markdown("##### 📋 Detalhamento por Recurso")
                    df_exibir_recursos = df_recursos.copy()
                    
                    # Formatar valores baseado na unidade
                    for idx, row in df_exibir_recursos.iterrows():
                        unidade = row['Unidade']
                        if unidade == 'R$':
                            df_exibir_recursos.at[idx, 'Disponível'] = f"R$ {row['Disponível']:,.0f}"
                            df_exibir_recursos.at[idx, 'Utilizado'] = f"R$ {row['Utilizado']:,.0f}"
                            df_exibir_recursos.at[idx, 'Não Utilizado'] = f"R$ {row['Não Utilizado']:,.0f}"
                        elif unidade in ['ha', 'm³', 'kg', 'h', 'ton']:
                            df_exibir_recursos.at[idx, 'Disponível'] = f"{row['Disponível']:,.0f} {unidade}"
                            df_exibir_recursos.at[idx, 'Utilizado'] = f"{row['Utilizado']:,.0f} {unidade}"
                            df_exibir_recursos.at[idx, 'Não Utilizado'] = f"{row['Não Utilizado']:,.0f} {unidade}"
                        df_exibir_recursos.at[idx, 'Utilização'] = f"{row['Utilização']:.1f}%"
                    
                    df_exibir_recursos = df_exibir_recursos.drop('Unidade', axis=1)
                    st.dataframe(df_exibir_recursos, width='stretch', hide_index=True)
                    
                    # Insights sobre recursos não utilizados
                    st.markdown("##### 💡 Insights sobre Recursos")
                    
                    # Recursos críticos (mais de 90% utilizados)
                    recursos_criticos = df_recursos[df_recursos['Utilização'] > 90]
                    if not recursos_criticos.empty:
                        recursos_lista = recursos_criticos['Recurso'].tolist()
                        st.warning(f"⚠️ **Recursos críticos:** {', '.join(recursos_lista)} estão sendo utilizados em mais de 90%. Considere aumentar esses recursos para potencial maior lucro.")
                    
                    # Recursos subutilizados (menos de 50% utilizados)
                    recursos_sub = df_recursos[df_recursos['Utilização'] < 50]
                    if not recursos_sub.empty:
                        recursos_lista = recursos_sub['Recurso'].tolist()
                        st.info(f"ℹ️ **Recursos subutilizados:** {', '.join(recursos_lista)} têm capacidade disponível. Você poderia expandir a produção se desejar.")
                    
                    # Melhor oportunidade de investimento
                    if not df_recursos.empty:
                        melhor_oportunidade = df_recursos.loc[df_recursos['Utilização'].idxmax()]
                        if melhor_oportunidade['Utilização'] < 100:
                            st.success(f"🎯 **Melhor oportunidade:** Aumentar {melhor_oportunidade['Recurso']} poderia gerar mais lucro, pois está {100-melhor_oportunidade['Utilização']:.1f}% disponível.")
                
                # NOVO: Análise de Preços Sombra
                if res.get('shadow_prices'):
                    shadow_prices = res['shadow_prices']
                    
                    st.markdown("##### 🎯 Análise de Preços Sombra")
                    st.markdown("""
                    **O que são preços sombra?**  
                    Indicam quanto o lucro total aumentaria se você tivesse uma unidade adicional de cada recurso restritivo.
                    """)
                    
                    # Mapeamento de restrições para nomes amigáveis
                    nomes_restricoes = {
                        'Restricao_Area_Total': {'nome': 'Área Total Disponível', 'unidade': 'R$/ha adicional', 'icone': '🌾'},
                        'Restricao_Area_Nao_Compactada': {'nome': 'Área Não Compactada', 'unidade': 'R$/ha adicional', 'icone': '🌱'},
                        'Restricao_Orcamento': {'nome': 'Orçamento Total', 'unidade': 'R$/R$ adicional', 'icone': '💰'},
                        'Restricao_Agua': {'nome': 'Água Disponível', 'unidade': 'R$/m³ adicional', 'icone': '💧'},
                        'Restricao_Potassio': {'nome': 'Potássio Disponível', 'unidade': 'R$/kg adicional', 'icone': '🧪'},
                        'Restricao_Fosforo': {'nome': 'Fósforo Disponível', 'unidade': 'R$/kg adicional', 'icone': '🧫'},
                        'Restricao_Horas_Maquina': {'nome': 'Horas de Máquina', 'unidade': 'R$/hora adicional', 'icone': '🚜'},
                        'Restricao_Armazenagem': {'nome': 'Capacidade do Silo', 'unidade': 'R$/ton adicional', 'icone': '🏭'},
                        'Minimo_Soja_Resistente': {'nome': 'Mínimo Soja Resistente', 'unidade': 'R$/ha a menos', 'icone': '🌾'},
                        'Minimo_Soja_Produtiva': {'nome': 'Mínimo Soja Produtiva', 'unidade': 'R$/ha a menos', 'icone': '🌾'},
                        'Minimo_Milho_Safrinha': {'nome': 'Mínimo Milho Safrinha', 'unidade': 'R$/ha a menos', 'icone': '🌽'},
                        'Risco_Maximo_Soja_Produtiva': {'nome': 'Máximo Soja Produtiva', 'unidade': 'R$/ha a mais', 'icone': '⚠️'}
                    }
                    
                    # Filtrar apenas preços sombra positivos (restrições ativas)
                    precos_ativos = {k: v for k, v in shadow_prices.items() if v is not None and v > 0.01}
                    
                    if precos_ativos:
                        dados_sombra = []
                        for restricao, preco in precos_ativos.items():
                            if restricao in nomes_restricoes:
                                info = nomes_restricoes[restricao]
                                dados_sombra.append({
                                    'Restrição': f"{info['icone']} {info['nome']}",
                                    'Preço Sombra': preco,
                                    'Unidade': info['unidade']
                                })
                        
                        if dados_sombra:
                            df_sombra = pd.DataFrame(dados_sombra)
                            
                            # Gráfico de barras para preços sombra
                            fig_sombra = px.bar(
                                df_sombra,
                                x='Restrição',
                                y='Preço Sombra',
                                title='💰 Preços Sombra - Valor de Relaxar Restrições',
                                color='Preço Sombra',
                                color_continuous_scale='Reds',
                                text='Preço Sombra'
                            )
                            fig_sombra.update_traces(texttemplate='R$ %{text:.2f}')
                            fig_sombra.update_layout(showlegend=False)
                            st.plotly_chart(fig_sombra, width='stretch')
                            
                            # Tabela detalhada
                            df_exibir_sombra = df_sombra.copy()
                            df_exibir_sombra['Preço Sombra'] = df_exibir_sombra['Preço Sombra'].apply(lambda x: f"R$ {x:.2f}")
                            df_exibir_sombra = df_exibir_sombra.drop('Unidade', axis=1)
                            st.dataframe(df_exibir_sombra, width='stretch', hide_index=True)
                            
                            # Recomendação baseada nos preços sombra
                            if not df_sombra.empty:
                                melhor_investimento = df_sombra.loc[df_sombra['Preço Sombra'].idxmax()]
                                st.success(f"🎯 **Melhor investimento:** Relaxar a restrição '{melhor_investimento['Restrição']}' geraria R$ {melhor_investimento['Preço Sombra']:.2f} de lucro adicional por unidade.")
                                
                                # Explicação adicional
                                st.info("""
                                **Como usar esta informação:**
                                - 📈 **Preços sombra altos**: Indicam restrições críticas que limitam seu lucro
                                - 💡 **Invista primeiro**: Nos recursos com maiores preços sombra
                                - 🎯 **ROI garantido**: Cada unidade adicional desses recursos gera lucro extra
                                """)
                        else:
                            st.info("ℹ️ Nenhuma restrição ativa encontrada. Todos os recursos estão disponíveis em abundância.")
                    else:
                        st.info("ℹ️ Nenhuma restrição ativa encontrada. A solução ótima não está limitada por recursos.")
                
                st.markdown("---")
                
                # Plano de plantio - VISUALIZAÇÃO MELHORADA
                st.markdown("#### 🌾 Seu Plano de Plantio")
                
                plantio = res['plantio']
                # Limpa nomes das culturas
                plantio_limpo = {}
                for k, v in plantio.items():
                    nome = k.replace('Hectares_', '').replace('_', ' ').title()
                    plantio_limpo[nome] = v
                
                df_plantio = pd.DataFrame(list(plantio_limpo.items()), columns=['Cultura', 'Hectares'])
                df_plantio['Porcentagem'] = (df_plantio['Hectares'] / df_plantio['Hectares'].sum() * 100).round(1)
                df_plantio = df_plantio.sort_values('Hectares', ascending=False)
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    # Pizza melhorada
                    fig_pie = px.pie(
                        df_plantio,
                        values='Hectares',
                        names='Cultura',
                        title='🥧 Distribuição por Cultura',
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_pie.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate='<b>%{label}</b><br>Área: %{value:.1f} ha<br>%{percent}<extra></extra>'
                    )
                    fig_pie.update_layout(showlegend=True, height=400)
                    st.plotly_chart(fig_pie, width='stretch')
                
                with col_b:
                    # Barras melhoradas
                    fig_bar = px.bar(
                        df_plantio,
                        x='Cultura',
                        y='Hectares',
                        title='📊 Área por Cultura (hectares)',
                        color='Hectares',
                        color_continuous_scale='Greens',
                        text='Hectares'
                    )
                    fig_bar.update_traces(
                        texttemplate='%{text:.1f} ha',
                        textposition='outside'
                    )
                    fig_bar.update_layout(showlegend=False, height=400)
                    st.plotly_chart(fig_bar, width='stretch')
                
                # Tabela detalhada
                st.markdown("#### 📋 Detalhamento por Cultura")
                df_plantio_exibir = df_plantio.copy()
                df_plantio_exibir['Hectares'] = df_plantio_exibir['Hectares'].apply(lambda x: f"{x:.2f}")
                df_plantio_exibir['Porcentagem'] = df_plantio_exibir['Porcentagem'].apply(lambda x: f"{x:.1f}%")
                st.dataframe(df_plantio_exibir, width='stretch', hide_index=True)
                
                # Insights automáticos
                st.markdown("---")
                st.markdown("#### 💡 Insights")
                
                cultura_dominante = df_plantio.iloc[0]
                if cultura_dominante['Porcentagem'] > 50:
                    st.warning(f"⚠️ A cultura **{cultura_dominante['Cultura']}** domina o plantio com {cultura_dominante['Porcentagem']:.1f}%. Considere diversificar para reduzir riscos.")
                elif cultura_dominante['Porcentagem'] > 40:
                    st.info(f"ℹ️ A cultura **{cultura_dominante['Cultura']}** é a principal ({cultura_dominante['Porcentagem']:.1f}%), mas há boa diversificação.")
                else:
                    st.success(f"✅ Plano bem diversificado! Cultura principal **{cultura_dominante['Cultura']}** representa {cultura_dominante['Porcentagem']:.1f}% do plantio.")
                
            else:
                st.error(f"❌ Otimização falhou: {res['status']}")
                if res.get('error'):
                    st.error(f"Erro: {res['error']}")

# Tab 3: Com Clima - INTEGRADO COM LOCALIZAÇÃO SELECIONADA
with tabs[2]:
    st.header("🌦️ Otimização com Análise Climática")
    
    st.markdown("""
    **Como funciona:** Esta otimização ajusta a produtividade esperada baseada em dados climáticos históricos da sua região.
    """)
    
    # NOVO: Verificar se há localização selecionada da página 03
    if 'localizacao_selecionada' in st.session_state:
        loc_sel = st.session_state.localizacao_selecionada
        st.info(f"📍 **Localização selecionada:** {loc_sel['cidade']}, {loc_sel['estado']} (Lat: {loc_sel['lat']:.4f}, Lon: {loc_sel['lon']:.4f})")
        
        usar_localizacao_personalizada = st.checkbox(
            "Usar localização selecionada da análise climática",
            value=True,
            help="Se desmarcado, usa as coordenadas definidas em cada cenário"
        )
    else:
        st.warning("⚠️ **Nenhuma localização selecionada.** Vá para a página 'Análise Climática' e selecione uma cidade primeiro.")
        usar_localizacao_personalizada = False
    
    # Explicação
    with st.expander("❓ O que é ajuste climático?", expanded=False):
        st.markdown("""
        ### 🌍 Por que considerar o clima?
        O clima afeta **diretamente** a produtividade das culturas:
        - 🌧️ **Precipitação**: Chuva demais ou de menos reduz produção
        - 🌡️ **Temperatura**: Cada cultura tem temperatura ideal
        - ☀️ **Radiação solar**: Influencia fotossíntese
        
        ### 📊 Como ajustamos?
        1. Buscamos dados históricos da sua localização
        2. Comparamos com valores ideais para cada cultura
        3. Ajustamos a produtividade esperada (ex: -15% em ano de seca)
        4. Executamos a otimização com valores mais realistas
        
        ### 🎯 Resultado:
        Um plano de plantio que considera as **condições reais** do clima da sua região.
        """)
    
    st.markdown("---")
    
    # Seleção de cenários
    st.subheader("1️⃣ Escolha os Cenários")
    
    scenarios_clima = manager.list_scenarios()
    
    # Mostra info dos cenários disponíveis
    st.markdown("**Cenários disponíveis:**")
    scenario_info = []
    for name in scenarios_clima:
        try:
            cfg = manager.load_scenario(name)
            cfg_dict = OmegaConf.to_container(cfg, resolve=True)
            loc = cfg_dict.get('location', {})
            scenario_info.append({
                "Cenário": name,
                "Lat": loc.get('lat', -12.5449),
                "Lon": loc.get('lon', -55.7126),
                "Anos": loc.get('years', 2)
            })
        except:
            pass
    
    if scenario_info:
        import pandas as pd
        st.dataframe(pd.DataFrame(scenario_info), hide_index=True, width='stretch')
    
    selected_clima = st.multiselect(
        "Selecione até 3 cenários para comparar:",
        scenarios_clima,
        max_selections=3,
        key="sel_clima",
        help="Escolha cenários com diferentes condições climáticas"
    )
    
    st.markdown("---")
    
    # Botão de execução
    st.subheader("2️⃣ Execute a Otimização")
    
    if not selected_clima:
        st.info("👆 Selecione pelo menos um cenário acima para começar")
    
    if st.button("🚀 Executar com Ajuste Climático", type="primary", disabled=not selected_clima):
        with st.spinner("🔄 Buscando dados climáticos e otimizando..."):
            resultados_clima = []
            
            for name in selected_clima:
                try:
                    cfg = manager.load_scenario(name)
                    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
                    
                    # NOVO: Usar localização personalizada se selecionada
                    if usar_localizacao_personalizada and 'localizacao_selecionada' in st.session_state:
                        loc_sel = st.session_state.localizacao_selecionada
                        lat = loc_sel['lat']
                        lon = loc_sel['lon']
                        cidade_display = f"{loc_sel['cidade']}, {loc_sel['estado']}"
                        st.info(f"🌍 Usando localização personalizada: {cidade_display}")
                    else:
                        # Usa coordenadas do cenário
                        loc = cfg_dict.get('location', {})
                        lat = loc.get('lat', -12.5449)
                        lon = loc.get('lon', -55.7126)
                        cidade_display = f"Coordenadas do cenário ({lat:.4f}, {lon:.4f})"
                    
                    # Busca dados climáticos
                    clima_res = climate.buscar_dados_clima(
                        lat=lat,
                        lon=lon,
                        years=loc.get('years', 2),
                        media_historica=loc.get('media_historica', 600.0)
                    )
                    
                    # Executa otimização
                    opt_res = run_optimization(cfg_dict, verbose=False)
                    
                    resultados_clima.append({
                        'Cenário': name,
                        'Localização': cidade_display,
                        'Lat': lat,
                        'Lon': lon,
                        'Lucro': opt_res.get('lucro'),
                        'Fator Climático': clima_res.get('fator'),
                        'Interpretação': climate.interpretar_fator_clima(clima_res.get('fator'))
                    })
                    
                except Exception as e:
                    st.error(f"❌ Erro em {name}: {e}")
            
            st.markdown("---")
            
            # Resultados
            if resultados_clima:
                st.subheader("📊 Resultados com Ajuste Climático")
                
                df_clima = pd.DataFrame(resultados_clima)
                
                # Gráfico principal
                col1, col2 = st.columns(2)
                
                with col1:
                    # Comparação de lucro - Barras
                    fig_lucro = px.bar(
                        df_clima,
                        x='Cenário',
                        y='Lucro',
                        title='💰 Lucro por Cenário (ajustado pelo clima)',
                        color='Lucro',
                        color_continuous_scale='RdYlGn',
                        text='Lucro'
                    )
                    fig_lucro.update_traces(
                        texttemplate='R$ %{text:,.0f}',
                        textposition='outside'
                    )
                    fig_lucro.update_layout(showlegend=False)
                    st.plotly_chart(fig_lucro, width='stretch')
                
                with col2:
                    # NOVO: Gráfico de linha conectando os lucros
                    fig_linha = px.line(
                        df_clima,
                        x='Cenário',
                        y='Lucro',
                        title='📈 Comparação de Lucros - Visão Linear',
                        markers=True,
                        line_shape='linear'
                    )
                    fig_linha.update_traces(
                        mode='lines+markers+text',
                        text=df_clima['Cenário'],
                        textposition='top center',
                        hovertemplate='<b>%{text}</b><br>Lucro: R$ %{y:,.0f}<extra></extra>'
                    )
                    fig_linha.update_layout(
                        xaxis_title="Cenários",
                        yaxis_title="Lucro (R$)",
                        showlegend=False
                    )
                    # Adicionar valores sobre os pontos
                    for i, row in df_clima.iterrows():
                        fig_linha.add_annotation(
                            x=row['Cenário'],
                            y=row['Lucro'],
                            text=f"R$ {row['Lucro']:,.0f}",
                            showarrow=False,
                            yshift=10,
                            font=dict(size=10, color='black')
                        )
                    st.plotly_chart(fig_linha, width='stretch')
                
                # Scatter plot em uma linha separada
                st.markdown("#### 🌦️ Análise Climática Detalhada")
                fig_scatter = px.scatter(
                    df_clima,
                    x='Fator Climático',
                    y='Lucro',
                    color='Cenário',
                    size='Lucro',
                    title='Impacto do Clima no Lucro por Cenário',
                    hover_data=['Interpretação', 'Localização']
                )
                fig_scatter.update_layout(
                    xaxis_title="Fator Climático (quanto mais próximo de 1, melhor)",
                    yaxis_title="Lucro Estimado (R$)"
                )
                st.plotly_chart(fig_scatter, width='stretch')
                
                # Tabela detalhada
                st.markdown("#### 📋 Análise Detalhada")
                df_exibir = df_clima.copy()
                df_exibir['Lucro'] = df_exibir['Lucro'].apply(lambda x: f"R$ {x:,.2f}")
                df_exibir['Fator Climático'] = df_exibir['Fator Climático'].apply(lambda x: f"{x:.2f}")
                st.dataframe(df_exibir, hide_index=True, width='stretch')
                
                # Insights
                st.markdown("---")
                st.markdown("#### 💡 Interpretação")
                
                melhor_cenario = df_clima.loc[df_clima['Lucro'].idxmax()]
                pior_cenario = df_clima.loc[df_clima['Lucro'].idxmin()]
                
                st.success(f"🏆 **Melhor cenário:** {melhor_cenario['Cenário']} com lucro de R$ {melhor_cenario['Lucro']:,.2f}")
                st.info(f"📊 **Fator climático:** {melhor_cenario['Fator Climático']:.2f} - {melhor_cenario['Interpretação']}")
                st.info(f"📍 **Localização:** {melhor_cenario['Localização']}")
                
                if len(df_clima) > 1:
                    diferenca = ((melhor_cenario['Lucro'] - pior_cenario['Lucro']) / pior_cenario['Lucro'] * 100)
                    st.warning(f"⚠️ **Diferença:** O melhor cenário gera {diferenca:.1f}% mais lucro que o pior ({pior_cenario['Cenário']})")
                    
                    # Explicação sobre fator climático
                    st.markdown("""
                    **Como interpretar o Fator Climático:**
                    - ✅ **1.0 ou mais**: Condições ideais ou melhores que a média
                    - ⚠️ **0.8 - 0.99**: Condições boas, pequeno ajuste negativo
                    - 🔴 **Abaixo de 0.8**: Condições ruins, impacto significativo na produtividade
                    """)
            else:
                st.info("ℹ️ Nenhum resultado para exibir. Execute a otimização acima.")
