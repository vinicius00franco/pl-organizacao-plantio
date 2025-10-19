"""
Utilitários para trabalhar com cenários.
Funções de conveniência para acesso rápido aos cenários.
"""

from typing import Dict, List, Any
from omegaconf import DictConfig, OmegaConf
from src.config import get_scenario_manager, AppConfig


def get_all_scenario_names() -> List[str]:
    """
    Retorna lista com nomes de todos os cenários disponíveis.
    
    Returns:
        Lista de nomes de cenários
    """
    manager = get_scenario_manager()
    return manager.list_scenarios()


def load_scenario(scenario_name: str) -> Dict[str, Any]:
    """
    Carrega um cenário completo (mergeado com base).
    
    Args:
        scenario_name: Nome do cenário
    
    Returns:
        Dicionário com configuração completa
    """
    manager = get_scenario_manager()
    cfg = manager.load_scenario(scenario_name)
    return OmegaConf.to_container(cfg, resolve=True)


def get_scenario_params(scenario_name: str) -> Dict[str, Any]:
    """
    Retorna apenas os parâmetros de um cenário.
    
    Args:
        scenario_name: Nome do cenário
    
    Returns:
        Dicionário com parâmetros (preços, percentuais, etc.)
    """
    scenario = load_scenario(scenario_name)
    return scenario.get('params', {})


def get_scenario_resources(scenario_name: str) -> Dict[str, Any]:
    """
    Retorna apenas os recursos de um cenário.
    
    Args:
        scenario_name: Nome do cenário
    
    Returns:
        Dicionário com recursos disponíveis
    """
    scenario = load_scenario(scenario_name)
    return scenario.get('resources', {})


def get_scenario_location(scenario_name: str) -> Dict[str, Any]:
    """
    Retorna apenas a localização de um cenário.
    
    Args:
        scenario_name: Nome do cenário
    
    Returns:
        Dicionário com informações de localização
    """
    scenario = load_scenario(scenario_name)
    return scenario.get('location', {})


def compare_scenarios(scenario_names: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Compara múltiplos cenários retornando suas configurações.
    
    Args:
        scenario_names: Lista de nomes de cenários
    
    Returns:
        Dicionário {nome_cenario: configuração}
    """
    return {name: load_scenario(name) for name in scenario_names}


def get_scenario_diff_from_base(scenario_name: str) -> Dict[str, Any]:
    """
    Retorna apenas as diferenças de um cenário em relação à base.
    
    Args:
        scenario_name: Nome do cenário
    
    Returns:
        Dicionário com diferenças
    """
    manager = get_scenario_manager()
    return manager.get_scenario_diff(scenario_name)


def create_scenario_from_template(
    scenario_name: str,
    description: str = "",
    params: Dict[str, Any] = None,
    resources: Dict[str, Any] = None,
    location: Dict[str, Any] = None,
    overwrite: bool = False
) -> Dict[str, Any]:
    """
    Cria um novo cenário a partir de um template com valores fornecidos.
    
    Args:
        scenario_name: Nome do novo cenário
        description: Descrição do cenário
        params: Parâmetros customizados (usa padrão se None)
        resources: Recursos customizados (usa padrão se None)
        location: Localização customizada (usa padrão se None)
        overwrite: Se True, sobrescreve cenário existente
    
    Returns:
        Dicionário com o cenário criado
    """
    manager = get_scenario_manager()
    
    # Cria template base
    template = AppConfig.get_default_scenario_template()
    template["_description"] = description or f"Cenário {scenario_name}"
    
    # Atualiza com valores customizados
    if params:
        template["params"].update(params)
    if resources:
        template["resources"].update(resources)
    if location:
        template["location"].update(location)
    
    # Salva cenário
    manager.save_scenario(scenario_name, template, overwrite=overwrite)
    
    return template


def validate_scenario_config(config: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Valida se uma configuração de cenário está completa e correta.
    
    Args:
        config: Configuração do cenário
    
    Returns:
        Tupla (is_valid, list_of_errors)
    """
    errors = []
    
    # Verifica estrutura básica
    if "params" not in config:
        errors.append("Falta seção 'params'")
    else:
        required_params = ["preco_soja", "preco_milho"]
        for param in required_params:
            if param not in config["params"]:
                errors.append(f"Falta parâmetro obrigatório: {param}")
    
    if "location" not in config:
        errors.append("Falta seção 'location'")
    else:
        required_location = ["lat", "lon"]
        for loc in required_location:
            if loc not in config["location"]:
                errors.append(f"Falta informação de localização: {loc}")
    
    # resources é opcional
    
    return len(errors) == 0, errors


def get_scenario_summary_all() -> List[Dict[str, Any]]:
    """
    Retorna resumo de todos os cenários disponíveis.
    
    Returns:
        Lista de dicionários com resumos
    """
    manager = get_scenario_manager()
    scenarios = manager.list_scenarios()
    
    summaries = []
    for name in scenarios:
        try:
            summary = manager.get_scenario_summary(name)
            summaries.append(summary)
        except Exception as e:
            summaries.append({
                'nome': name,
                'erro': str(e)
            })
    
    return summaries


def clear_scenario_cache():
    """Limpa o cache de cenários."""
    manager = get_scenario_manager()
    manager.clear_cache()
