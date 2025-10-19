"""
Aplicação Streamlit - Otimização do Mix de Culturas
Sistema completo para gestão de cenários, análise climática e otimização de plantio.
"""

import streamlit as st
from pathlib import Path
import sys

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Configuração da página
st.set_page_config(
    page_title="Otimização de Plantio",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E7D32;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E7D32;
    }
    .stAlert {
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Página principal da aplicação."""
    
    # Header
    st.markdown('<div class="main-header">Sistema de Otimizacao de Plantio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Gestão Inteligente de Cenários e Análise Climática</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/2E7D32/FFFFFF?text=AgroTech", width='stretch')
        st.markdown("---")
        st.markdown("### Navegacao")
        st.markdown("""
        Use o menu acima para acessar:
        - **Dados da Fazenda**: Importar e visualizar dados
        - **Análise Financeira**: Dados econômicos (IPCA, SELIC, Dólar)
        - **Análise Climática**: Consultar dados climáticos
        - **Cenários**: Gerenciar cenários de plantio
        - **Otimização**: Executar e comparar cenários
        - **Relatórios**: Visualizar resultados e gargalos
        """)
        st.markdown("---")
        st.markdown("### ℹ️ Sobre")
        st.info("""
        Sistema integrado para otimização do mix de culturas,
        considerando recursos disponíveis, preços de mercado
        e condições climáticas.
        """)
    
    # Conteúdo principal
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Dados da Fazenda",
            value="Importar CSV",
            delta="Configure seus talhões"
        )
        st.markdown("Importe dados reais da sua propriedade ou use dados simulados para análise.")
        if st.button("Acessar Dados", key="btn_dados", width='stretch'):
            st.switch_page("pages/01_dados_fazenda.py")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Análise Financeira",
            value="Dados BC",
            delta="IPCA, SELIC, Dólar"
        )
        st.markdown("Análise inteligente de indicadores econômicos para ajustar preços e custos.")
        if st.button("Acessar Financeiro", key="btn_financeiro", width='stretch'):
            st.switch_page("pages/06_analise_financeira.py")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Clima",
            value="Analisar",
            delta="Dados históricos"
        )
        st.markdown("Consulte dados climáticos por estado, cidade ou coordenadas geográficas.")
        if st.button("Acessar Clima", key="btn_clima", width='stretch'):
            st.switch_page("pages/03_analise_clima.py")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Segunda linha de cards
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Cenários",
            value="Gerenciar",
            delta="Criar e editar"
        )
        st.markdown("Visualize, edite e crie novos cenários de plantio com diferentes parâmetros.")
        if st.button("Acessar Cenários", key="btn_cenarios", width='stretch'):
            st.switch_page("pages/02_cenarios.py")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Otimizacao",
            value="Executar",
            delta="Planos de plantio"
        )
        st.markdown("Execute a otimização para cada cenário e visualize os planos de plantio recomendados.")
        if st.button("Acessar Otimização", key="btn_otim", width='stretch'):
            st.switch_page("pages/04_otimizacao.py")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col6:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="Relatorios",
            value="Visualizar",
            delta="Análise completa"
        )
        st.markdown("Visualize relatórios comparativos, preços sombra e identifique gargalos de recursos.")
        if st.button("Acessar Relatórios", key="btn_rel", width='stretch'):
            st.switch_page("pages/05_relatorios.py")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Guia rápido
    with st.expander("Guia Rapido de Uso", expanded=False):
        st.markdown("""
        ### Como usar o sistema:
        
        1. **Importe seus dados** (ou use dados simulados)
           - Va para "Dados da Fazenda"
           - Faca upload de um CSV ou gere dados mock
        
        2. **Analise dados financeiros**
           - Acesse "Análise Financeira"
           - Busque dados do Banco Central (IPCA, SELIC, Dólar)
           - Veja soluções inteligentes baseadas nos indicadores
        
        3. **Analise o clima**
           - Va para "Analise Climatica"
           - Consulte dados por cidade ou coordenadas
           - Compare diferentes localizacoes
        
        4. **Configure cenarios**
           - Acesse "Cenários"
           - Visualize os cenarios existentes (base, agressivo, conservador, etc.)
           - Aplique ajustes financeiros automaticamente
        
        5. **Execute a otimizacao**
           - Va para "Otimizacao"
           - Selecione cenarios para executar
           - Visualize os planos de plantio recomendados
        
        6. **Analise os resultados**
           - Acesse "Relatorios"
           - Compare cenarios
           - Identifique gargalos e oportunidades
        """)
    
    # Informações técnicas
    with st.expander("Informacoes Tecnicas", expanded=False):
        st.markdown("""
        ### Tecnologias utilizadas:
        - **Streamlit**: Interface web interativa
        - **PuLP**: Otimização linear
        - **Pandas**: Manipulação de dados
        - **Plotly**: Gráficos interativos
        - **Meteostat**: Dados climáticos históricos
        - **OmegaConf**: Gerenciamento de configurações
        
        ### Modelo de otimização:
        - Maximização do lucro total
        - Restrições de recursos (área, orçamento, água, nutrientes)
        - Diversificação de culturas (mínimos por cultura)
        - Gestão de risco (máximos para culturas mais arriscadas)
        """)

if __name__ == "__main__":
    main()
