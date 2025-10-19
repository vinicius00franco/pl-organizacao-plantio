"""
Página de Relatórios e Análise Comparativa
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

st.set_page_config(page_title="Relatórios", page_icon="📈", layout="wide")

st.title("Relatórios e Análises")
st.markdown("Visualize comparações, preços sombra e identifique gargalos.")

if 'resultados' not in st.session_state or not st.session_state.resultados:
    st.warning("Nenhum resultado disponível. Execute cenários na página de Otimização primeiro.")
else:
    tabs = st.tabs(["Comparativo", "Preços Sombra", "Gargalos", "Análise Detalhada"])
    
    resultados = st.session_state.resultados
    
    # Tab 1: Comparativo
    with tabs[0]:
        st.header("Comparação Entre Cenários")
        
        # Prepara dados comparativos
        dados_comp = []
        for name, res in resultados.items():
            if res['status'] == 'Optimal':
                dados_comp.append({
                    'Cenário': name,
                    'Lucro Total': res['lucro'],
                    'Lucro/ha': res.get('metricas', {}).get('lucro_por_hectare', 0),
                    'Área Plantada': res.get('metricas', {}).get('area_total_plantada', 0),
                    'Taxa Uso': res.get('metricas', {}).get('taxa_utilizacao_area', 0)
                })
        
        if dados_comp:
            df_comp = pd.DataFrame(dados_comp)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(df_comp, x='Cenário', y='Lucro Total',
                           title='Lucro Total por Cenário',
                           color='Lucro Total',
                           color_continuous_scale='Greens')
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                fig = px.bar(df_comp, x='Cenário', y='Lucro/ha',
                           title='Lucro por Hectare',
                           color='Lucro/ha',
                           color_continuous_scale='Blues')
                st.plotly_chart(fig, width='stretch')
            
            # Plantio por cenário
            st.subheader("Distribuição de Plantio")
            
            plantio_comp = []
            for name, res in resultados.items():
                if res['status'] == 'Optimal':
                    for cultura, hectares in res['plantio'].items():
                        cultura_nome = cultura.replace('Hectares_', '').replace('_', ' ')
                        plantio_comp.append({
                            'Cenário': name,
                            'Cultura': cultura_nome,
                            'Hectares': hectares
                        })
            
            if plantio_comp:
                df_plantio = pd.DataFrame(plantio_comp)
                
                fig = px.bar(df_plantio, x='Cenário', y='Hectares', color='Cultura',
                           title='Área Plantada por Cultura e Cenário',
                           barmode='stack')
                st.plotly_chart(fig, width='stretch')
    
    # Tab 2: Preços Sombra
    with tabs[1]:
        st.header("Análise de Preços Sombra")
        
        st.markdown("""
        **Preços sombra** indicam quanto o lucro aumentaria se você tivesse uma unidade adicional de cada recurso.
        Valores altos indicam recursos que são gargalos críticos.
        """)
        
        cenario_sel = st.selectbox("Selecione um cenário", list(resultados.keys()), key="shadow_select")
        
        if cenario_sel:
            res = resultados[cenario_sel]
            
            if res['status'] == 'Optimal' and res.get('shadow_prices'):
                shadow = res['shadow_prices']
                
                # Filtra apenas restrições com preço sombra significativo
                shadow_data = []
                for nome, valor in shadow.items():
                    if valor and abs(valor) > 0.01:
                        nome_legivel = nome.replace('Restricao_', '').replace('_', ' ')
                        shadow_data.append({
                            'Restrição': nome_legivel,
                            'Preço Sombra': valor,
                            'Impacto': 'Alto' if abs(valor) > 100 else 'Médio' if abs(valor) > 10 else 'Baixo'
                        })
                
                if shadow_data:
                    df_shadow = pd.DataFrame(shadow_data)
                    df_shadow = df_shadow.sort_values('Preço Sombra', key=abs, ascending=False)
                    
                    st.dataframe(df_shadow, width='stretch')
                    
                    fig = px.bar(df_shadow, x='Restrição', y='Preço Sombra',
                               color='Impacto',
                               title='Preços Sombra por Restrição',
                               color_discrete_map={'Alto': 'red', 'Médio': 'orange', 'Baixo': 'green'})
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.info("Nenhum preço sombra significativo encontrado.")
    
    # Tab 3: Gargalos
    with tabs[2]:
        st.header("Identificação de Gargalos")
        
        st.markdown("""
        Gargalos são recursos que limitam sua produção. Investir nestes recursos
        terá o maior impacto no lucro total.
        """)
        
        cenario_garg = st.selectbox("Selecione um cenário", list(resultados.keys()), key="garg_select")
        
        if cenario_garg:
            res = resultados[cenario_garg]
            
            if res['status'] == 'Optimal' and res.get('shadow_prices'):
                # Identifica top gargalos
                gargalos = []
                for nome, valor in res['shadow_prices'].items():
                    if valor and valor > 0.01:
                        nome_limpo = nome.replace('Restricao_', '').replace('_', ' ')
                        gargalos.append({
                            'Recurso': nome_limpo,
                            'Valor Marginal (R$)': valor,
                            'Prioridade': 1 if valor > 100 else 2 if valor > 10 else 3
                        })
                
                if gargalos:
                    df_garg = pd.DataFrame(gargalos).sort_values('Valor Marginal (R$)', ascending=False)
                    
                    st.subheader("Top Gargalos (Prioridade de Investimento)")
                    
                    top_5 = df_garg.head(5)
                    
                    for idx, row in top_5.iterrows():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.markdown(f"**{row['Recurso']}**")
                        with col2:
                            st.metric("Valor Marginal", f"R$ {row['Valor Marginal (R$)']:.2f}")
                        with col3:
                            prioridade = "Alta" if row['Prioridade'] == 1 else "Média" if row['Prioridade'] == 2 else "Baixa"
                            st.markdown(prioridade)
                        st.markdown("---")
                    
                    # Gráfico de Pareto
                    df_garg['Acumulado %'] = df_garg['Valor Marginal (R$)'].cumsum() / df_garg['Valor Marginal (R$)'].sum() * 100
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=df_garg['Recurso'],
                        y=df_garg['Valor Marginal (R$)'],
                        name='Valor Marginal',
                        marker_color='indianred'
                    ))
                    fig.add_trace(go.Scatter(
                        x=df_garg['Recurso'],
                        y=df_garg['Acumulado %'],
                        name='Acumulado %',
                        yaxis='y2',
                        line=dict(color='blue', width=2)
                    ))
                    fig.update_layout(
                        title='Análise de Pareto - Gargalos',
                        yaxis=dict(title='Valor Marginal (R$)'),
                        yaxis2=dict(title='Acumulado %', overlaying='y', side='right'),
                        barmode='group'
                    )
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.info("Nenhum gargalo crítico identificado.")
    
    # Tab 4: Análise Detalhada
    with tabs[3]:
        st.header("Análise Detalhada")
        
        cenario_det = st.selectbox("Selecione um cenário", list(resultados.keys()), key="det_select")
        
        if cenario_det:
            res = resultados[cenario_det]
            
            if res['status'] == 'Optimal':
                st.subheader("Informações Completas")
                
                # Métricas principais
                col1, col2, col3, col4, col5 = st.columns(5)
                metricas = res.get('metricas', {})
                
                with col1:
                    st.metric("Lucro Total", f"R$ {res['lucro']:,.0f}")
                with col2:
                    st.metric("Área Total", f"{metricas.get('area_total_plantada', 0):.1f} ha")
                with col3:
                    st.metric("Lucro/ha", f"R$ {metricas.get('lucro_por_hectare', 0):,.0f}")
                with col4:
                    st.metric("Taxa Uso", f"{metricas.get('taxa_utilizacao_area', 0):.1f}%")
                with col5:
                    st.metric("Status", res['status'])
                
                # Detalhamento do plantio
                st.subheader("Plano de Plantio Detalhado")
                
                plantio_det = []
                for cultura, hectares in res['plantio'].items():
                    cultura_nome = cultura.replace('Hectares_', '').replace('_', ' ')
                    params = res.get('params_agregados', {})
                    
                    if cultura_nome in params:
                        p = params[cultura_nome]
                        plantio_det.append({
                            'Cultura': cultura_nome,
                            'Área (ha)': hectares,
                            '% do Total': hectares / metricas.get('area_total_plantada', 1) * 100,
                            'Produtividade (t/ha)': p.get('produtividade_ton_ha', 0),
                            'Custo/ha (R$)': p.get('custo_ha', 0),
                            'Lucro/ha (R$)': p.get('lucro_ha', 0),
                            'Lucro Total (R$)': hectares * p.get('lucro_ha', 0)
                        })
                
                if plantio_det:
                    df_det = pd.DataFrame(plantio_det)
                    st.dataframe(df_det.style.format({
                        'Área (ha)': '{:.2f}',
                        '% do Total': '{:.1f}%',
                        'Produtividade (t/ha)': '{:.2f}',
                        'Custo/ha (R$)': 'R$ {:,.2f}',
                        'Lucro/ha (R$)': 'R$ {:,.2f}',
                        'Lucro Total (R$)': 'R$ {:,.2f}'
                    }), width='stretch')
                    
                    # Download
                    csv = df_det.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Baixar Plano Detalhado (CSV)",
                        data=csv,
                        file_name=f"plano_plantio_{cenario_det}.csv",
                        mime="text/csv"
                    )
