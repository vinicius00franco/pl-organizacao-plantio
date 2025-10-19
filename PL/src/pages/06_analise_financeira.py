"""
Página de Análise Financeira com RAG
"""

import streamlit as st
from pathlib import Path
import sys

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.services.analise_financeira_rag import AnaliseFinanceiraRAG
from src.config import get_scenario_manager
from omegaconf import OmegaConf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análise Financeira", page_icon="💰", layout="wide")

st.title("💰 Análise Financeira com IA")
st.markdown("Análise inteligente dos indicadores econômicos para otimizar decisões agrícolas.")

# Inicializar serviço
rag_service = AnaliseFinanceiraRAG()

# Interface principal
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🔄 Coletar Dados Financeiros")

    anos = st.slider("Anos de histórico", 1, 5, 2)

    if st.button("📊 Buscar Dados do BC"):
        with st.spinner("Buscando dados do Banco Central..."):
            df_financeiro = rag_service.coletar_dados_financeiros(anos)
            if not df_financeiro.empty:
                st.session_state.df_financeiro = df_financeiro
                # salvar origens por indicador (cache vs bcb)
                try:
                    st.session_state.df_financeiro_sources = rag_service.last_sources.copy()
                except Exception:
                    st.session_state.df_financeiro_sources = {}
                st.success("✅ Dados coletados com sucesso!")
                st.rerun()
            else:
                st.error("❌ Erro ao coletar dados.")

with col2:
    if 'df_financeiro' in st.session_state:
        df = st.session_state.df_financeiro

        # Gráficos dos indicadores (separados por unidade)
        st.subheader("📈 Indicadores Financeiros")

        # IPCA (%)
        fig_ipca = px.line(df, x=df.index, y='IPCA', title='📉 IPCA (Inflação) — %')
        fig_ipca.update_layout(height=240, yaxis_title='IPCA (%)')
        st.plotly_chart(fig_ipca, width='stretch')
        # Fonte do dado
        src_ipca = st.session_state.get('df_financeiro_sources', {}).get('IPCA', 'desconhecida')
        st.caption(f"Fonte: {'Cache (Redis)' if src_ipca == 'cache' else 'BCB' if src_ipca == 'bcb' else src_ipca}")

        # SELIC (%)
        fig_selic = px.line(df, x=df.index, y='SELIC', title='📈 SELIC — % (Taxa de Juros)')
        fig_selic.update_layout(height=240, yaxis_title='SELIC (%)')
        st.plotly_chart(fig_selic, width='stretch')
        src_selic = st.session_state.get('df_financeiro_sources', {}).get('SELIC', 'desconhecida')
        st.caption(f"Fonte: {'Cache (Redis)' if src_selic == 'cache' else 'BCB' if src_selic == 'bcb' else src_selic}")

        # Dólar (R$)
        fig_dolar = px.line(df, x=df.index, y='Dolar', title='💱 Dólar PTAX — R$')
        fig_dolar.update_layout(height=240, yaxis_title='Dólar (R$)')
        st.plotly_chart(fig_dolar, width='stretch')
        src_dolar = st.session_state.get('df_financeiro_sources', {}).get('Dolar', 'desconhecida')
        st.caption(f"Fonte: {'Cache (Redis)' if src_dolar == 'cache' else 'BCB' if src_dolar == 'bcb' else src_dolar}")

        # Métricas atuais
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("IPCA Atual", f"{df['IPCA'].iloc[-1]:.2f}%")
        with col2:
            st.metric("SELIC Média 6M", f"{df['SELIC'].iloc[-180:].mean():.2f}%")
        with col3:
            st.metric("Dólar Médio 6M", f"R$ {df['Dolar'].iloc[-180:].mean():.2f}")

# Análise RAG
if 'df_financeiro' in st.session_state:
    st.markdown("---")
    st.header("🤖 Análise Inteligente com RAG")

    # Base de conhecimento
    knowledge = rag_service.criar_base_conhecimento(st.session_state.df_financeiro)

    with st.expander("📚 Base de Conhecimento Gerada"):
        st.text_area("Contexto Financeiro", knowledge, height=200)

    # Gerar soluções
    st.subheader("💡 Soluções Inteligentes Recomendadas")

    solucoes = rag_service.gerar_solucoes_inteligentes(knowledge, dados_financeiros=st.session_state.df_financeiro)

    for i, sol in enumerate(solucoes, 1):
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**{i}. {sol['titulo']}**")
                st.write(sol['descricao'])
                st.info(f"🎯 **Ação:** {sol['acao']}")
                st.success(f"✅ **Benefício:** {sol['beneficio']}")
                st.warning(f"⚠️ **Risco:** {sol['risco']}")

            with col2:
                prioridade_cores = {'Alta': '🔴', 'Média': '🟡', 'Baixa': '🟢'}
                st.metric("Prioridade", f"{prioridade_cores[sol['prioridade']]} {sol['prioridade']}")

                if st.button(f"Aplicar #{i}", key=f"apply_{i}"):
                    st.success(f"✅ Solução {i} aplicada ao sistema!")

    # Integração com cenários
    st.markdown("---")
    st.subheader("🔗 Integração com Cenários de Otimização")

    st.info("""
    💡 **Como usar:** As soluções acima podem ser aplicadas automaticamente aos seus cenários.
    Por exemplo, ajustes de preço por inflação serão refletidos nos parâmetros dos cenários.
    """)

    if st.button("🚀 Aplicar Ajustes aos Cenários"):
        # Aplica ajustes financeiros criando novos cenários ajustados (não sobrescreve)
        manager = get_scenario_manager()
        df_fin = st.session_state.df_financeiro

        # Extrai indicadores
        ipca_val = float(df_fin['IPCA'].iloc[-1]) if 'IPCA' in df_fin.columns else 0.0
        selic_val = float(df_fin['SELIC'].iloc[-180:].mean()) if 'SELIC' in df_fin.columns else 0.0
        dolar_val = float(df_fin['Dolar'].iloc[-180:].mean()) if 'Dolar' in df_fin.columns else 0.0

        created = []
        for name in manager.list_scenarios():
            # Criar cenário ajustado também para o 'base' (se desejar) e para todos os demais

            # Carrega cenário mergeado para obter parâmetros atuais
            try:
                cfg = manager.load_scenario(name)
                cfg_dict = OmegaConf.to_container(cfg, resolve=True)
            except Exception:
                cfg_dict = manager.get_scenario_diff(name) or {}

            params = cfg_dict.get('params', {}) or {}

            # Aplicar ajustes simples baseados nos indicadores
            preco_soja = float(params.get('preco_soja', 2200))
            preco_milho = float(params.get('preco_milho', 1300))

            # Ajuste por inflação (80% do IPCA)
            mult_inflacao = 1 + (ipca_val / 100.0) * 0.8 if ipca_val else 1.0
            novo_preco_soja = round(preco_soja * mult_inflacao)
            novo_preco_milho = round(preco_milho * mult_inflacao)

            # Ajuste adicional por câmbio — beneficia commodities exportáveis (soja)
            if dolar_val and dolar_val > 5.2:
                novo_preco_soja = round(novo_preco_soja * 1.15)

            # Ajuste de custos (exemplo simples: reduzir custo de produção com eficiência se SELIC alta)
            # Não sobrescrevemos recursos aqui, apenas ajustamos preços

            # Monta novo cenário com apenas diffs (params)
            novo_nome_base = f"{name}_financeiro"
            novo_nome = novo_nome_base
            idx = 1
            while True:
                try:
                    new_config = {
                        "# @package _group_": None,
                        "params": {
                            "preco_soja": int(novo_preco_soja),
                            "preco_milho": int(novo_preco_milho),
                            "percentual_minimo_por_cultura": params.get('percentual_minimo_por_cultura', 0.15),
                            "percentual_maximo_soja_produtiva": params.get('percentual_maximo_soja_produtiva', 0.60)
                        }
                    }

                    # Tenta salvar; se existir, incrementa sufixo _financeiro_1, _2, ...
                    manager.save_scenario(novo_nome, new_config, overwrite=False)
                    created.append(novo_nome)
                    break
                except FileExistsError:
                    # gera novo nome com índice incremental
                    novo_nome = f"{novo_nome_base}_{idx}"
                    idx += 1
                    # continue loop e tente novamente
                except Exception as e:
                    st.error(f"Erro ao salvar cenário ajustado para {name}: {e}")
                    break

        if created:
            st.success(f"✅ Ajustes financeiros aplicados — {len(created)} cenários criados:")
            st.write(created)
            st.info("Agora vá para 'Otimização' para ver os resultados atualizados.")
        else:
            st.info("ℹ️ Nenhum cenário foi criado (possívelmente já existiam cenários ajustados).")