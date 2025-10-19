"""
Análise Financeira com RAG para Otimização Agrícola
"""

from bcb import sgs
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import streamlit as st
import os
import json

try:
    import redis
except Exception:
    redis = None

class AnaliseFinanceiraRAG:
    """Sistema RAG para análise financeira agrícola"""

    def __init__(self):
        self.codigos_sgs = {
            'IPCA': 433,      # Inflação
            'SELIC': 11,      # Taxa de juros
            'Dolar': 1        # Câmbio PTAX
        }
        # Guarda a origem dos dados por indicador após coleta
        # ex: {'IPCA': 'cache', 'SELIC': 'bcb'}
        self.last_sources = {}

    def coletar_dados_financeiros(self, anos_historico: int = 2) -> pd.DataFrame:
        """Coleta dados financeiros do Banco Central"""
        end = datetime.now()
        start = datetime(end.year - anos_historico, end.month, end.day)
        cache_ttl = 60 * 60 * 3  # 3 horas em segundos

        # Vamos montar um DataFrame vazio que será preenchido
        results = {}

        # Tenta usar Redis se disponível
        r = None
        if redis is not None:
            try:
                redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
                r = redis.from_url(redis_url, socket_connect_timeout=2)
            except Exception as e:
                print(f"⚠️ Redis não disponível: {e}")

        # Para cada indicador, tentamos ler cache por chave individual
        for indicador, codigo in self.codigos_sgs.items():
            key = f"financeiro:{indicador}:historico:{anos_historico}"
            used_cache = False
            if r is not None:
                try:
                    cached = r.get(key)
                    if cached:
                        try:
                            cached_str = cached.decode('utf-8') if isinstance(cached, (bytes, bytearray)) else str(cached)
                            serie = pd.read_json(cached_str, typ='series', orient='split')
                            results[indicador] = serie
                            self.last_sources[indicador] = 'cache'
                            used_cache = True
                        except Exception:
                            # parsing falhou -> ignorar cache
                            used_cache = False
                except Exception:
                    # leitura cache falhou -> ignorar
                    used_cache = False

            if not used_cache:
                # buscar diretamente do BCB só para este indicador
                try:
                    print(f"🔄 Buscando {indicador} do Banco Central...")
                    s = sgs.get({indicador: codigo}, start=start, end=end)
                    # s vem como DataFrame de 1 coluna. Extraímos a série.
                    if not s.empty:
                        serie = s[indicador]
                        results[indicador] = serie
                        self.last_sources[indicador] = 'bcb'

                        # armazena no cache individual se possível
                        if r is not None:
                            try:
                                # serializa a Series como JSON orient='split'
                                json_str = serie.to_json(date_format='iso', orient='split')
                                r.setex(key, cache_ttl, json_str)
                                print(f"✅ {indicador} armazenado em cache (Redis)")
                            except Exception as e:
                                print(f"⚠️ Não foi possível salvar {indicador} no Redis: {e}")
                    else:
                        results[indicador] = pd.Series(dtype=float)
                        self.last_sources[indicador] = 'bcb'
                except Exception as e:
                    print(f"❌ Erro ao coletar {indicador}: {e}")
                    results[indicador] = pd.Series(dtype=float)
                    self.last_sources[indicador] = 'error'

        # Monta DataFrame final a partir das séries coletadas
        try:
            df = pd.DataFrame(results)
            # organiza o index como datetime quando possível
            if df.index.dtype == object:
                try:
                    df.index = pd.to_datetime(df.index)
                except Exception:
                    pass
            print("✅ Dados financeiros agregados com sucesso!")
            return df
        except Exception as e:
            print(f"❌ Erro ao agregar resultados: {e}")
            return pd.DataFrame()

    def criar_base_conhecimento(self, df_financeiro: pd.DataFrame) -> str:
        """Cria base de conhecimento textual para RAG"""

        if df_financeiro.empty:
            return "Dados financeiros não disponíveis."

        # Cálculos recentes
        ultimo_ipca = df_financeiro['IPCA'].iloc[-1] if not df_financeiro['IPCA'].empty else 0
        media_selic_6m = df_financeiro['SELIC'].iloc[-180:].mean() if len(df_financeiro) >= 180 else df_financeiro['SELIC'].mean()
        media_dolar_6m = df_financeiro['Dolar'].iloc[-180:].mean() if len(df_financeiro) >= 180 else df_financeiro['Dolar'].mean()

        # Tendências
        tendencia_ipca = "crescente" if df_financeiro['IPCA'].iloc[-30:].mean() > df_financeiro['IPCA'].iloc[-90:-30].mean() else "decrescente"
        tendencia_dolar = "crescente" if df_financeiro['Dolar'].iloc[-30:].mean() > df_financeiro['Dolar'].iloc[-90:-30].mean() else "decrescente"

        knowledge_base = f"""
        RELATÓRIO DE ANÁLISE FINANCEIRA PARA AGRONEGÓCIO - {datetime.now().strftime('%d/%m/%Y')}

        INFLAÇÃO (IPCA):
        - Último valor: {ultimo_ipca:.2f}%
        - Tendência: {tendencia_ipca}
        - Impacto agrícola: Inflação alta aumenta custos de insumos (fertilizantes, defensivos, combustível)

        JUROS (SELIC):
        - Média últimos 6 meses: {media_selic_6m:.2f}%
        - Impacto agrícola: Juros elevados encarecem crédito rural e financiamentos

        CÂMBIO (DÓLAR PTAX):
        - Média últimos 6 meses: R$ {media_dolar_6m:.2f}
        - Tendência: {tendencia_dolar}
        - Impacto agrícola: Dólar alto favorece exportações de soja e milho

        CONTEXTO ECONÔMICO ATUAL:
        - Ambiente {'inflacionário' if ultimo_ipca > 5 else 'de baixa inflação'}
        - Crédito {'restritivo' if media_selic_6m > 10 else 'acessível'}
        - Exportações {'favoráveis' if media_dolar_6m > 5 else 'desfavoráveis'}
        """

        return knowledge_base

    def gerar_solucoes_inteligentes(self, knowledge_base: str, contexto_agricola: Dict = None, dados_financeiros: pd.DataFrame = None) -> List[Dict]:
        """Gera 5 soluções inteligentes baseadas nos dados financeiros"""

        # Extrair valores diretamente dos dados financeiros se disponíveis
        if dados_financeiros is not None and not dados_financeiros.empty:
            ipca = dados_financeiros['IPCA'].iloc[-1] if not dados_financeiros['IPCA'].empty else 5.0
            selic = dados_financeiros['SELIC'].iloc[-180:].mean() if len(dados_financeiros) >= 180 else dados_financeiros['SELIC'].mean() if not dados_financeiros['SELIC'].empty else 10.0
            dolar = dados_financeiros['Dolar'].iloc[-180:].mean() if len(dados_financeiros) >= 180 else dados_financeiros['Dolar'].mean() if not dados_financeiros['Dolar'].empty else 5.0
        else:
            # Fallback: tentar extrair do texto (menos robusto)
            try:
                linhas = knowledge_base.split('\n')
                ipca = float([l.split(':')[1].strip().replace('%', '') for l in linhas if 'Último valor:' in l][0])
                selic = float([l.split(':')[1].strip().replace('%', '') for l in linhas if 'Média últimos 6 meses:' in l and 'SELIC' in l][0])
                dolar = float([l.split(':')[1].strip().replace('R$', '').strip() for l in linhas if 'Média últimos 6 meses:' in l and 'Dólar' in l][0])
            except (IndexError, ValueError):
                # Valores padrão se parsing falhar
                ipca, selic, dolar = 5.0, 10.0, 5.0

        # Contexto agrícola (pode vir dos cenários)
        if contexto_agricola is None:
            contexto_agricola = {
                'preco_soja_atual': 2200,
                'custo_producao_ha': 2500,
                'margem_atual': -300  # prejuízo
            }

        solucoes = []

        # Solução 1: Ajuste de preços baseado na inflação
        if ipca > 5:
            ajuste_preco = 1 + (ipca / 100) * 0.8  # 80% da inflação
            novo_preco = contexto_agricola['preco_soja_atual'] * ajuste_preco
            impacto = (novo_preco - contexto_agricola['preco_soja_atual']) * 1000  # por ha
            solucoes.append({
                'titulo': '🔄 Ajuste de Preços por Inflação',
                'descricao': f'Ajustar preços de venda em {ipca:.1f}% devido à inflação alta',
                'acao': f'Aumentar preço da soja para R$ {novo_preco:.0f}/ton (+R$ {impacto:.0f}/ha)',
                'beneficio': f'Impacto positivo de R$ {impacto:.0f} por hectare',
                'risco': 'Baixo - necessário para cobrir custos inflacionários',
                'prioridade': 'Alta' if ipca > 8 else 'Média'
            })

        # Solução 2: Otimização de custos com juros altos
        if selic > 8:
            reducao_custo = contexto_agricola['custo_producao_ha'] * 0.05  # 5% economia
            economia_anual = reducao_custo * 100  # assumindo 100 ha
            solucoes.append({
                'titulo': '💰 Otimização de Custos com Juros Elevados',
                'descricao': 'Reduzir custos operacionais para compensar juros altos no crédito',
                'acao': f'Implementar plano de redução de custos em 5% (R$ {reducao_custo:.0f}/ha)',
                'beneficio': f'Economia de R$ {economia_anual:.0f} em 100 hectares',
                'risco': 'Médio - requer eficiência operacional',
                'prioridade': 'Alta'
            })

        # Solução 3: Estratégia de exportação com dólar favorável
        if dolar > 5.2:
            premio_exportacao = contexto_agricola['preco_soja_atual'] * 0.15  # 15% prêmio
            receita_extra = premio_exportacao * 1000  # por ha
            solucoes.append({
                'titulo': '🌍 Estratégia de Exportação com Dólar Favorável',
                'descricao': 'Aproveitar câmbio favorável para exportações',
                'acao': f'Destinar 30% da produção para exportação (prêmio de R$ {premio_exportacao:.0f}/ton)',
                'beneficio': f'Receita extra de R$ {receita_extra:.0f} por hectare',
                'risco': 'Alto - depende de logística internacional',
                'prioridade': 'Alta' if dolar > 5.5 else 'Média'
            })

        # Solução 4: Diversificação de culturas para hedge inflacionário
        solucoes.append({
            'titulo': '🌾 Diversificação para Proteção Inflacionária',
            'descricao': 'Diversificar culturas para reduzir risco inflacionário',
            'acao': 'Aumentar participação de milho safrinha (menos sensível à inflação)',
            'beneficio': 'Redução de risco de 15-20% em cenários inflacionários',
            'risco': 'Baixo - estratégia de diversificação',
            'prioridade': 'Média'
        })

        # Solução 5: Planejamento financeiro integrado
        economia_juros = contexto_agricola['custo_producao_ha'] * 0.03 * (selic / 100)  # economia com planejamento
        solucoes.append({
            'titulo': '📊 Planejamento Financeiro Integrado',
            'descricao': 'Integrar dados financeiros na tomada de decisão agrícola',
            'acao': f'Usar análise financeira para ajustar orçamento (+R$ {economia_juros:.0f}/ha economia)',
            'beneficio': 'Decisões mais precisas e redução de custos financeiros',
            'risco': 'Baixo - melhoria de processo',
            'prioridade': 'Alta'
        })

        return solucoes

    def analisar_cenario_com_financeiro(self, cenario: Dict, dados_financeiros: pd.DataFrame) -> Dict:
        """Analisa um cenário específico com dados financeiros"""

        knowledge = self.criar_base_conhecimento(dados_financeiros)
        solucoes = self.gerar_solucoes_inteligentes(knowledge, cenario)

        return {
            'contexto_financeiro': knowledge,
            'solucoes_recomendadas': solucoes,
            'resumo_economico': {
                'ipca_atual': dados_financeiros['IPCA'].iloc[-1],
                'selic_media': dados_financeiros['SELIC'].iloc[-180:].mean(),
                'dolar_medio': dados_financeiros['Dolar'].iloc[-180:].mean()
            }
        }