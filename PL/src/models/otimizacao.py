"""
Módulo de otimização do mix de culturas.
Extraído do notebook otimizacao_mix_culturas_v5_organized.ipynb
"""

import pandas as pd
import numpy as np
from pulp import LpProblem, LpVariable, LpMaximize, lpSum, value, LpStatus
from typing import Dict, Tuple, Optional, Any
from datetime import datetime
import json


def generate_mock_data(n_dados: int = 1500, seed: int = 42, verbose: bool = False) -> pd.DataFrame:
    """
    Gera dados mock de talhões para simulação.
    
    Args:
        n_dados: Número de talhões a gerar
        seed: Seed para reprodutibilidade
        verbose: Se True, imprime estatísticas
    
    Returns:
        DataFrame com dados dos talhões
    """
    np.random.seed(int(seed))
    df = pd.DataFrame({
        'id_talhao': range(1, n_dados + 1),
        'cultura': np.random.choice(['Soja_Resistente', 'Soja_Produtiva', 'Milho_Safrinha'], n_dados)
    })

    culturas_params = {
        'Soja_Resistente': {
            'prod': (3.5, 0.5), 'custo': (1800, 150), 'agua': (450, 50),
            'k': (80, 10), 'p': (70, 8), 'horas': (10, 1.5)
        },
        'Soja_Produtiva': {
            'prod': (4.8, 0.6), 'custo': (2500, 200), 'agua': (600, 60),
            'k': (100, 12), 'p': (90, 10), 'horas': (12, 1.8)
        },
        'Milho_Safrinha': {
            'prod': (5.5, 0.7), 'custo': (2800, 250), 'agua': (700, 70),
            'k': (120, 15), 'p': (100, 12), 'horas': (15, 2.0)
        },
    }

    def gen(params, size):
        return {
            'produtividade_ton_ha': np.random.normal(loc=params['prod'][0], scale=params['prod'][1], size=size),
            'custo_ha': np.random.normal(loc=params['custo'][0], scale=params['custo'][1], size=size),
            'uso_agua_m3_ha': np.random.normal(loc=params['agua'][0], scale=params['agua'][1], size=size),
            'demanda_k_kg_ha': np.random.normal(loc=params['k'][0], scale=params['k'][1], size=size),
            'demanda_p_kg_ha': np.random.normal(loc=params['p'][0], scale=params['p'][1], size=size),
            'horas_maquina_ha': np.random.normal(loc=params['horas'][0], scale=params['horas'][1], size=size),
        }

    for cultura, params in culturas_params.items():
        mask = df['cultura'] == cultura
        data = gen(params, mask.sum())
        for k, vals in data.items():
            df.loc[mask, k] = vals

    if verbose:
        print(f"Dados mock gerados: {len(df)} talhões")
        print(df['cultura'].value_counts())

    return df


def setup_model_from_params(
    params_df: pd.DataFrame,
    resources: Dict[str, float],
    percentual_minimo_por_cultura: float = 0.15,
    percentual_maximo_soja_produtiva: float = 0.60
) -> Tuple[LpProblem, Tuple[LpVariable, LpVariable, LpVariable]]:
    """
    Configura o modelo de programação linear.
    
    Args:
        params_df: DataFrame com parâmetros médios por cultura
        resources: Dicionário com recursos disponíveis
        percentual_minimo_por_cultura: Mínimo por cultura (diversificação)
        percentual_maximo_soja_produtiva: Máximo para soja produtiva (risco)
    
    Returns:
        Tupla (modelo, variáveis_de_decisão)
    """
    modelo = LpProblem(name='Otimizacao_Mix_Culturas', sense=LpMaximize)
    
    # Variáveis de decisão
    x_sr = LpVariable('Hectares_Soja_Resistente', lowBound=0, cat='Continuous')
    x_sp = LpVariable('Hectares_Soja_Produtiva', lowBound=0, cat='Continuous')
    x_ms = LpVariable('Hectares_Milho_Safrinha', lowBound=0, cat='Continuous')

    def val(cultura, col):
        try:
            return float(params_df.at[cultura, col])
        except Exception:
            return 0.0

    # Parâmetros por cultura
    l_sr = val('Soja_Resistente', 'lucro_ha')
    l_sp = val('Soja_Produtiva', 'lucro_ha')
    l_ms = val('Milho_Safrinha', 'lucro_ha')
    
    c_sr = val('Soja_Resistente', 'custo_ha')
    c_sp = val('Soja_Produtiva', 'custo_ha')
    c_ms = val('Milho_Safrinha', 'custo_ha')
    
    a_sr = val('Soja_Resistente', 'uso_agua_m3_ha')
    a_sp = val('Soja_Produtiva', 'uso_agua_m3_ha')
    a_ms = val('Milho_Safrinha', 'uso_agua_m3_ha')
    
    k_sr = val('Soja_Resistente', 'demanda_k_kg_ha')
    k_sp = val('Soja_Produtiva', 'demanda_k_kg_ha')
    k_ms = val('Milho_Safrinha', 'demanda_k_kg_ha')
    
    p_sr = val('Soja_Resistente', 'demanda_p_kg_ha')
    p_sp = val('Soja_Produtiva', 'demanda_p_kg_ha')
    p_ms = val('Milho_Safrinha', 'demanda_p_kg_ha')
    
    h_sr = val('Soja_Resistente', 'horas_maquina_ha')
    h_sp = val('Soja_Produtiva', 'horas_maquina_ha')
    h_ms = val('Milho_Safrinha', 'horas_maquina_ha')
    
    prod_sr = val('Soja_Resistente', 'produtividade_ton_ha')
    prod_sp = val('Soja_Produtiva', 'produtividade_ton_ha')
    prod_ms = val('Milho_Safrinha', 'produtividade_ton_ha')

    # Gestão de risco
    area_nc = float(resources.get('AREA_NAO_COMPACTADA_HA', 0))
    area_minima_ha = int(area_nc * float(percentual_minimo_por_cultura))
    area_maxima_sp = int(area_nc * float(percentual_maximo_soja_produtiva))

    # Restrições de diversificação e risco
    modelo += (x_sr >= area_minima_ha, 'Minimo_Soja_Resistente')
    modelo += (x_sp >= area_minima_ha, 'Minimo_Soja_Produtiva')
    modelo += (x_ms >= area_minima_ha, 'Minimo_Milho_Safrinha')
    modelo += (x_sp <= area_maxima_sp, 'Risco_Maximo_Soja_Produtiva')

    # Função objetivo
    modelo += lpSum([l_sr * x_sr, l_sp * x_sp, l_ms * x_ms]), 'Lucro_Total'

    # Restrições de recursos
    modelo += (x_sr + x_sp + x_ms <= resources.get('AREA_TOTAL_DISPONIVEL_HA', 0), 'Restricao_Area_Total')
    modelo += (x_sr + x_sp + x_ms <= resources.get('AREA_NAO_COMPACTADA_HA', 0), 'Restricao_Area_Nao_Compactada')
    modelo += (c_sr * x_sr + c_sp * x_sp + c_ms * x_ms <= resources.get('ORCAMENTO_TOTAL_DISPONIVEL', 0), 'Restricao_Orcamento')
    modelo += (a_sr * x_sr + a_sp * x_sp + a_ms * x_ms <= resources.get('AGUA_TOTAL_DISPONIVEL_M3', 0), 'Restricao_Agua')
    modelo += (k_sr * x_sr + k_sp * x_sp + k_ms * x_ms <= resources.get('POTASSIO_DISPONIVEL_KG', 0), 'Restricao_Potassio')
    modelo += (p_sr * x_sr + p_sp * x_sp + p_ms * x_ms <= resources.get('FOSFORO_DISPONIVEL_KG', 0), 'Restricao_Fosforo')
    modelo += (h_sr * x_sr + h_sp * x_sp + h_ms * x_ms <= resources.get('HORAS_MAQUINA_DISPONIVEIS', 0), 'Restricao_Horas_Maquina')
    modelo += (prod_sr * x_sr + prod_sp * x_sp + prod_ms * x_ms <= resources.get('CAPACIDADE_SILO_TON', 0), 'Restricao_Armazenagem')

    return modelo, (x_sr, x_sp, x_ms)


def run_optimization(cfg: Dict[str, Any], verbose: bool = False) -> Dict[str, Any]:
    """
    Executa a otimização com base em uma configuração de cenário.
    
    Args:
        cfg: Dicionário com 'params' e 'resources'
        verbose: Se True, imprime detalhes
    
    Returns:
        Dicionário com status, lucro, plantio e preços sombra
    """
    params_in = cfg.get('params', {})
    resources = cfg.get('resources', {})

    # Gera ou carrega dados
    df = generate_mock_data(
        int(params_in.get('n_dados', 1500)),
        int(params_in.get('seed', 42)),
        verbose=verbose
    )
    
    params = df.groupby('cultura').mean()
    
    # Calcula lucro por hectare
    preco_soja = float(params_in.get('preco_soja', 2200))
    preco_milho = float(params_in.get('preco_milho', 1300))
    
    params['lucro_ha'] = 0.0
    params.at['Soja_Resistente', 'lucro_ha'] = (
        params.at['Soja_Resistente', 'produtividade_ton_ha'] * preco_soja - 
        params.at['Soja_Resistente', 'custo_ha']
    )
    params.at['Soja_Produtiva', 'lucro_ha'] = (
        params.at['Soja_Produtiva', 'produtividade_ton_ha'] * preco_soja - 
        params.at['Soja_Produtiva', 'custo_ha']
    )
    params.at['Milho_Safrinha', 'lucro_ha'] = (
        params.at['Milho_Safrinha', 'produtividade_ton_ha'] * preco_milho - 
        params.at['Milho_Safrinha', 'custo_ha']
    )

    perc_min = float(params_in.get('percentual_minimo_por_cultura', 0.15))
    perc_max_sp = float(params_in.get('percentual_maximo_soja_produtiva', 0.60))

    modelo, variables = setup_model_from_params(
        params, resources,
        percentual_minimo_por_cultura=perc_min,
        percentual_maximo_soja_produtiva=perc_max_sp
    )

    try:
        solve_status = modelo.solve()
        status = LpStatus[modelo.status]
    except Exception as e:
        if verbose:
            print(f"Falha ao executar solver: {e}")
        return {
            'status': 'Error',
            'lucro': None,
            'plantio': None,
            'shadow_prices': None,
            'error': str(e)
        }

    plantio = {v.name: v.varValue for v in variables} if status == 'Optimal' else None
    shadow = {name: getattr(con, 'pi', None) for name, con in modelo.constraints.items()}

    results = {
        'status': status,
        'lucro': value(modelo.objective) if status == 'Optimal' else None,
        'plantio': plantio,
        'shadow_prices': shadow,
        'params_agregados': params.to_dict()
    }
    
    return results


def calcular_metricas(resultado: Dict[str, Any], resources: Dict[str, float]) -> Dict[str, Any]:
    """
    Calcula métricas adicionais do resultado de otimização.
    
    Args:
        resultado: Resultado da otimização
        resources: Recursos disponíveis
    
    Returns:
        Dicionário com métricas calculadas
    """
    if resultado['status'] != 'Optimal' or not resultado['plantio']:
        return {}
    
    plantio = resultado['plantio']
    total_area = sum(plantio.values())
    
    metricas = {
        'area_total_plantada': total_area,
        'taxa_utilizacao_area': total_area / resources.get('AREA_TOTAL_DISPONIVEL_HA', 1) * 100,
        'lucro_por_hectare': resultado['lucro'] / total_area if total_area > 0 else 0,
        'distribuicao_culturas': {
            k: (v / total_area * 100 if total_area > 0 else 0) 
            for k, v in plantio.items()
        }
    }
    
    return metricas


def calcular_recursos_utilizados(resultado: Dict[str, Any], resources: Dict[str, float], params_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula quanto de cada recurso foi utilizado vs disponível.
    
    Args:
        resultado: Resultado da otimização
        resources: Recursos disponíveis
        params_df: DataFrame com parâmetros por cultura
    
    Returns:
        Dicionário com análise de recursos
    """
    if resultado['status'] != 'Optimal' or not resultado['plantio']:
        return {}
    
    plantio = resultado['plantio']
    
    # Extrair valores das variáveis
    x_sr = plantio.get('Hectares_Soja_Resistente', 0)
    x_sp = plantio.get('Hectares_Soja_Produtiva', 0)
    x_ms = plantio.get('Hectares_Milho_Safrinha', 0)
    
    def val(cultura, col):
        try:
            return float(params_df.at[cultura, col])
        except Exception:
            return 0.0
    
    # Calcular recursos utilizados
    recursos_utilizados = {
        'AREA_TOTAL_DISPONIVEL_HA': x_sr + x_sp + x_ms,
        'ORCAMENTO_TOTAL_DISPONIVEL': (
            val('Soja_Resistente', 'custo_ha') * x_sr +
            val('Soja_Produtiva', 'custo_ha') * x_sp +
            val('Milho_Safrinha', 'custo_ha') * x_ms
        ),
        'AGUA_TOTAL_DISPONIVEL_M3': (
            val('Soja_Resistente', 'uso_agua_m3_ha') * x_sr +
            val('Soja_Produtiva', 'uso_agua_m3_ha') * x_sp +
            val('Milho_Safrinha', 'uso_agua_m3_ha') * x_ms
        ),
        'POTASSIO_DISPONIVEL_KG': (
            val('Soja_Resistente', 'demanda_k_kg_ha') * x_sr +
            val('Soja_Produtiva', 'demanda_k_kg_ha') * x_sp +
            val('Milho_Safrinha', 'demanda_k_kg_ha') * x_ms
        ),
        'FOSFORO_DISPONIVEL_KG': (
            val('Soja_Resistente', 'demanda_p_kg_ha') * x_sr +
            val('Soja_Produtiva', 'demanda_p_kg_ha') * x_sp +
            val('Milho_Safrinha', 'demanda_p_kg_ha') * x_ms
        ),
        'HORAS_MAQUINA_DISPONIVEIS': (
            val('Soja_Resistente', 'horas_maquina_ha') * x_sr +
            val('Soja_Produtiva', 'horas_maquina_ha') * x_sp +
            val('Milho_Safrinha', 'horas_maquina_ha') * x_ms
        ),
        'CAPACIDADE_SILO_TON': (
            val('Soja_Resistente', 'produtividade_ton_ha') * x_sr +
            val('Soja_Produtiva', 'produtividade_ton_ha') * x_sp +
            val('Milho_Safrinha', 'produtividade_ton_ha') * x_ms
        )
    }
    
    # Calcular recursos não utilizados e percentuais
    recursos_analise = {}
    for recurso, utilizado in recursos_utilizados.items():
        disponivel = resources.get(recurso, 0)
        nao_utilizado = disponivel - utilizado
        percentual_utilizado = (utilizado / disponivel * 100) if disponivel > 0 else 0
        
        recursos_analise[recurso] = {
            'disponivel': disponivel,
            'utilizado': utilizado,
            'nao_utilizado': nao_utilizado,
            'percentual_utilizado': percentual_utilizado,
            'percentual_nao_utilizado': 100 - percentual_utilizado
        }
    
    # Área não compactada (recurso especial para restrições de diversificação)
    area_nc_disponivel = resources.get('AREA_NAO_COMPACTADA_HA', 0)
    area_nc_utilizada = x_sr + x_sp + x_ms  # Mesmo que área total para este caso
    area_nc_nao_utilizada = area_nc_disponivel - area_nc_utilizada
    
    recursos_analise['AREA_NAO_COMPACTADA_HA'] = {
        'disponivel': area_nc_disponivel,
        'utilizado': area_nc_utilizada,
        'nao_utilizado': area_nc_nao_utilizada,
        'percentual_utilizado': (area_nc_utilizada / area_nc_disponivel * 100) if area_nc_disponivel > 0 else 0,
        'percentual_nao_utilizado': 100 - ((area_nc_utilizada / area_nc_disponivel * 100) if area_nc_disponivel > 0 else 0)
    }
    
    return recursos_analise
