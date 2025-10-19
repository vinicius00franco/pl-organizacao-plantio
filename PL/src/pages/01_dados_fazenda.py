"""
Página de Dados da Fazenda - Importação e Visualização de Dados
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.models.otimizacao import generate_mock_data

st.set_page_config(page_title="Dados da Fazenda", page_icon="📊", layout="wide")

st.title("Dados da Fazenda")
st.markdown("Importe dados dos seus talhões ou gere dados simulados para análise.")

# Inicializa session state
if 'dados_fazenda' not in st.session_state:
    st.session_state.dados_fazenda = None

tabs = st.tabs(["Importar Dados", "Gerar Dados Mock", "Visualizar Dados"])

# Tab 1: Importar CSV
with tabs[0]:
    st.header("Importar Dados de CSV")
    
    st.info("""
    **Formato esperado do CSV:**
    - `id_talhao`: Identificador único do talhão
    - `cultura`: Tipo de cultura (Soja_Resistente, Soja_Produtiva, Milho_Safrinha)
    - `produtividade_ton_ha`: Produtividade em toneladas por hectare
    - `custo_ha`: Custo por hectare (R$)
    - `uso_agua_m3_ha`: Consumo de água (m³/ha)
    - `demanda_k_kg_ha`: Demanda de potássio (kg/ha)
    - `demanda_p_kg_ha`: Demanda de fósforo (kg/ha)
    - `horas_maquina_ha`: Horas de máquina por hectare
    """)
    
    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Validação básica
            required_cols = ['id_talhao', 'cultura', 'produtividade_ton_ha', 'custo_ha', 
                           'uso_agua_m3_ha', 'demanda_k_kg_ha', 'demanda_p_kg_ha', 'horas_maquina_ha']
            
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"❌ Colunas faltando: {', '.join(missing_cols)}")
            else:
                st.success(f"✅ Arquivo carregado com sucesso! {len(df)} talhões encontrados.")
                
                st.subheader("Preview dos Dados")
                st.dataframe(df.head(10), width='stretch')
                
                if st.button("Salvar Dados", type="primary"):
                    st.session_state.dados_fazenda = df
                    st.success("Dados salvos com sucesso!")
                    st.rerun()
        
        except Exception as e:
            st.error(f"❌ Erro ao ler arquivo: {e}")

# Tab 2: Gerar dados mock
with tabs[1]:
    st.header("Gerar Dados Simulados")
    
    st.markdown("""
    Gere dados simulados para testar o sistema sem precisar de dados reais.
    Os dados são gerados seguindo distribuições normais baseadas em parâmetros típicos
    de culturas de soja e milho.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        n_dados = st.number_input(
            "Número de talhões",
            min_value=100,
            max_value=5000,
            value=1500,
            step=100,
            help="Quantidade de talhões a gerar"
        )
    
    with col2:
        seed = st.number_input(
            "Seed (reprodutibilidade)",
            min_value=1,
            max_value=9999,
            value=42,
            help="Use o mesmo seed para gerar os mesmos dados"
        )
    
    if st.button("Gerar Dados Mock", type="primary"):
        with st.spinner("Gerando dados..."):
            df = generate_mock_data(n_dados=n_dados, seed=seed, verbose=False)
            st.session_state.dados_fazenda = df
            st.success(f"✅ {len(df)} talhões gerados com sucesso!")
            st.rerun()

# Tab 3: Visualizar dados
with tabs[2]:
    st.header("Visualização dos Dados")
    
    if st.session_state.dados_fazenda is None:
        st.warning("⚠️ Nenhum dado carregado. Importe um CSV ou gere dados mock.")
    else:
        df = st.session_state.dados_fazenda
        
        # Estatísticas gerais
        st.subheader("Estatisticas Gerais")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Talhões", len(df))
        with col2:
            st.metric("Culturas", df['cultura'].nunique())
        with col3:
            prod_media = df['produtividade_ton_ha'].mean()
            st.metric("Produtividade Média", f"{prod_media:.2f} t/ha")
        with col4:
            custo_medio = df['custo_ha'].mean()
            st.metric("Custo Médio", f"R$ {custo_medio:,.0f}/ha")
        
        st.markdown("---")
        
        # Distribuição por cultura
        st.subheader("Distribuicao por Cultura")
        
        # Selecionar coluna para análise
        numeric_cols = ['produtividade_ton_ha', 'custo_ha', 'uso_agua_m3_ha', 'demanda_k_kg_ha', 'demanda_p_kg_ha', 'horas_maquina_ha']
        col = st.selectbox("Escolha uma variável para analisar:", numeric_cols, key="col_select")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            dist = df['cultura'].value_counts().reset_index()
            dist.columns = ['Cultura', 'Quantidade']
            st.dataframe(dist, width='stretch')
        
        with col2:
            fig = px.histogram(df, x=col, title=f'Distribuição de {col}')
            st.plotly_chart(fig, width='stretch')
        
        st.markdown("---")
        
        # Estatísticas por cultura
        st.subheader("Estatisticas por Cultura")
        
        stats = df.groupby('cultura').agg({
            'produtividade_ton_ha': ['mean', 'std'],
            'custo_ha': ['mean', 'std'],
            'uso_agua_m3_ha': 'mean',
            'demanda_k_kg_ha': 'mean',
            'demanda_p_kg_ha': 'mean',
            'horas_maquina_ha': 'mean'
        }).round(2)
        
        stats.columns = ['Produtividade Média', 'Produtividade DP', 
                        'Custo Médio', 'Custo DP',
                        'Água Média', 'Potássio Médio', 'Fósforo Médio', 'Horas Máquina']
        
        st.dataframe(stats, width='stretch')
        
        st.markdown("---")
        
        # Gráficos comparativos
        st.subheader("Comparacoes Visuais")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.box(df, y=col, title=f'Box Plot de {col}')
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            fig = px.box(
                df,
                x='cultura',
                y='custo_ha',
                title='Distribuição de Custo por Cultura',
                color='cultura',
                color_discrete_sequence=px.colors.sequential.Oranges
            )
            st.plotly_chart(fig, width='stretch')
        
        col3, col4 = st.columns(2)
        
        with col3:
            fig = px.scatter(
                df,
                x='produtividade_ton_ha',
                y='custo_ha',
                color='cultura',
                title='Relação Produtividade vs Custo',
                trendline="ols"
            )
            st.plotly_chart(fig, width='stretch')
        
        with col4:
            fig = px.scatter(
                df,
                x='uso_agua_m3_ha',
                y='produtividade_ton_ha',
                color='cultura',
                title='Uso de Água vs Produtividade'
            )
            st.plotly_chart(fig, width='stretch')
        
        st.markdown("---")
        
        # Dados brutos
        with st.expander("Ver Dados Brutos"):
            st.dataframe(df, width='stretch')
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Baixar Dados em CSV",
                data=csv,
                file_name="dados_fazenda.csv",
                mime="text/csv"
            )

# Seção de Integração Climática - ADICIONADO
st.markdown("---")
st.markdown("### 🌦️ Integração com Dados Climáticos")

if 'localizacao_selecionada' in st.session_state:
    loc = st.session_state.localizacao_selecionada
    st.success(f"✅ **Localização configurada:** {loc['cidade']}, {loc['estado']}")
    st.info("💡 Os dados climáticos desta localização serão usados para ajustar as produtividades na otimização.")
    
    # Mostrar resumo climático se disponível
    if 'resultado_clima' in st.session_state:
        clima = st.session_state.resultado_clima
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Fator Climático", f"{clima.get('fator', 'N/A'):.2f}")
        with col2:
            st.metric("Precip. Média", f"{clima.get('precip_media', 'N/A'):.1f} mm")
        with col3:
            st.metric("Anos Analisados", loc.get('years', 2))
        
        # Botão para ir para otimização
        st.markdown("---")
        if st.button("🚀 Ir para Otimização com Clima", type="primary"):
            st.switch_page("pages/04_otimizacao.py")
else:
    st.warning("⚠️ **Nenhuma localização climática selecionada.**")
    st.info("👉 Vá para a página 'Análise Climática' e selecione uma cidade para integrar dados climáticos ao seu plano de plantio.")
    
    # Botão para ir para análise climática
    if st.button("🌤️ Ir para Análise Climática", type="secondary"):
        st.switch_page("pages/03_analise_clima.py")
