"""
Página de Análise Climática
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.services.climate_service import ClimateService

st.set_page_config(page_title="Análise Climática", page_icon="🌤️", layout="wide")

st.title("Análise Climática")
st.markdown("Consulte dados climáticos históricos para planejar seu plantio.")

service = ClimateService()

tabs = st.tabs(["Por Cidade", "Por Coordenadas", "Comparar Localizações"])

# Tab 1: Por Cidade
with tabs[0]:
    st.header("Consulta por Cidade")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Lista completa de todos os estados brasileiros
        estados_disponiveis = [
            "Todos",
            "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
            "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
            "RS", "RO", "RR", "SC", "SP", "SE", "TO"
        ]
        
        # Selectbox de estado
        estado = st.selectbox(
            "Estado", 
            estados_disponiveis,
            key="select_estado"
        )
        
        # Filtra cidades pelo estado selecionado
        if estado == "Todos":
            cidades_dict = service.get_cidades_disponiveis()
        else:
            cidades_dict = service.get_cidades_disponiveis(estado)
        
        # Ordena as cidades alfabeticamente
        cidades_ordenadas = sorted(cidades_dict.keys())
        
        # Mostra informação de debug
        st.caption(f"{len(cidades_ordenadas)} cidade(s) disponível(is) em {estado}")
        
        # Selectbox de cidade
        cidade = st.selectbox(
            "Cidade", 
            cidades_ordenadas,
            key="select_cidade"
        )
        
        years = st.slider("Anos de histórico", 1, 5, 2)
        media_hist = st.number_input("Média histórica (mm)", value=600.0, step=10.0)
        
        if st.button("Buscar Dados"):
            with st.spinner("Consultando dados climáticos..."):
                # Busca coordenadas da cidade
                coords = cidades_dict[cidade]
                
                # Salva localização selecionada no session_state
                st.session_state.localizacao_selecionada = {
                    'estado': estado,
                    'cidade': cidade,
                    'lat': coords['lat'],
                    'lon': coords['lon'],
                    'years': years,
                    'media_historica': media_hist
                }
                
                # Busca dados climáticos
                resultado = service.buscar_dados_clima(
                    lat=coords['lat'],
                    lon=coords['lon'],
                    years=years,
                    media_historica=media_hist
                )
                
                st.session_state.resultado_clima = resultado
                st.success(f"✅ Dados encontrados para {cidade}, {estado}")
                st.info("💡 Esta localização agora está ativa para uso na otimização com ajuste climático!")
    
    with col2:
        if st.session_state.get('resultado_clima'):
            resultado = st.session_state.resultado_clima
            
            # Mostra informações da localização selecionada
            if 'localizacao_selecionada' in st.session_state:
                loc = st.session_state.localizacao_selecionada
                st.info(f"📍 **Localização ativa:** {loc['cidade']}, {loc['estado']} - pronta para usar na otimização!")
            
            # Mostra métricas principais
            col1, col2, col3 = st.columns(3)
            with col1:
                fator_val = resultado.get('fator', 'N/A')
                st.metric("Fator Climático", f"{fator_val:.3f}" if isinstance(fator_val, (int, float)) else str(fator_val))
            with col2:
                precip_val = resultado.get('precip_media', 'N/A')
                st.metric("Precip. Média", f"{precip_val:.1f} mm" if isinstance(precip_val, (int, float)) else str(precip_val))
            with col3:
                st.metric("Anos Analisados", years)
            
            # Interpretação
            st.info(service.interpretar_fator_clima(resultado.get('fator')))
            
            # Gráfico de precipitação se disponível
            if resultado.get('precipitacoes'):
                df = pd.DataFrame(resultado['precipitacoes'], columns=['Início', 'Fim', 'Precipitação (mm)'])
                
                fig = px.bar(df, x='Início', y='Precipitação (mm)', title='Precipitação por Safra')
                st.plotly_chart(fig, width='stretch')

# Tab 2: Por Coordenadas
with tabs[1]:
    st.header("Consulta por Coordenadas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        lat = st.number_input("Latitude", value=-12.5449, format="%.4f")
        years_coord = st.slider("Anos de histórico", 1, 5, 2, key="years_coord")
    
    with col2:
        lon = st.number_input("Longitude", value=-55.7126, format="%.4f")
        media_coord = st.number_input("Média histórica (mm)", value=600.0, step=10.0, key="media_coord")
    
    if st.button("Consultar", key="consultar_coord"):
        with st.spinner("Buscando dados..."):
            resultado = service.buscar_dados_clima(lat, lon, years_coord, media_coord)
            
            if resultado.get('error'):
                st.error(f"Erro: {resultado['error']}")
            else:
                fator = resultado.get('fator')
                summary = resultado.get('summary', {})
                
                st.success("Dados obtidos!")
                st.metric("Fator Climático", f"{fator:.3f}" if fator else "N/A")
                st.info(service.interpretar_fator_clima(fator))
                
                if resultado.get('precipitacoes'):
                    df = pd.DataFrame(resultado['precipitacoes'], columns=['Início', 'Fim', 'Precipitação (mm)'])
                    
                    fig = px.bar(df, x='Início', y='Precipitação (mm)', title='Precipitação por Safra')
                    st.plotly_chart(fig, width='stretch')

# Tab 3: Comparar
with tabs[2]:
    st.header("Comparar Múltiplas Localizações")
    
    st.markdown("Compare dados climáticos de diferentes propriedades ou regiões.")
    
    num_loc = st.number_input("Quantas localizações comparar?", 2, 5, 3)
    
    localizacoes = []
    for i in range(num_loc):
        with st.expander(f"Localização {i+1}", expanded=(i<2)):
            col1, col2, col3 = st.columns(3)
            with col1:
                nome = st.text_input(f"Nome", value=f"Local {i+1}", key=f"nome_{i}")
            with col2:
                lat_comp = st.number_input(f"Latitude", value=-12.5-i, format="%.4f", key=f"lat_{i}")
            with col3:
                lon_comp = st.number_input(f"Longitude", value=-55.7-i, format="%.4f", key=f"lon_{i}")
            
            localizacoes.append({'nome': nome, 'lat': lat_comp, 'lon': lon_comp, 'media_historica': 600.0})
    
    if st.button("Comparar", type="primary"):
        with st.spinner("Comparando localizações..."):
            df_comp = service.comparar_localizacoes(localizacoes, years=2)
            
            st.dataframe(df_comp, width='stretch')
            
            fig = px.bar(df_comp, x='nome', y='fator_clima', title='Fator Climático por Localização',
                        color='fator_clima', color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, width='stretch')
