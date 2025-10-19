"""
Configuração centralizada da aplicação.
Define paths, constantes e singleton para gerenciamento de cenários.
"""

from pathlib import Path
from typing import Optional
from src.services.scenario_manager import ScenarioManager


class AppConfig:
    """
    Configuração centralizada da aplicação.
    Singleton que garante uma única instância do ScenarioManager.
    """
    
    _instance: Optional['AppConfig'] = None
    _scenario_manager: Optional[ScenarioManager] = None
    
    # Paths da aplicação
    ROOT_DIR = Path(__file__).parent.parent.parent
    CONFIG_DIR = ROOT_DIR / "config"
    SCENARIO_DIR = CONFIG_DIR / "cenario"
    DATA_DIR = ROOT_DIR / "data"
    OUTPUTS_DIR = ROOT_DIR / "outputs"
    
    # Configurações de cenários
    SCENARIO_BASE_NAME = "base"
    
    # Configurações climáticas padrão
    DEFAULT_CLIMATE_CONFIG = {
        "lat": -12.5449,
        "lon": -55.7126,
        "years": 2,
        "media_historica": 600.0
    }
    
    # Configurações de recursos padrão
    DEFAULT_RESOURCES = {
        "AREA_TOTAL_DISPONIVEL_HA": 500,
        "ORCAMENTO_TOTAL_DISPONIVEL": 1100000,
        "AGUA_TOTAL_DISPONIVEL_M3": 250000,
        "POTASSIO_DISPONIVEL_KG": 45000,
        "FOSFORO_DISPONIVEL_KG": 42000,
        "HORAS_MAQUINA_DISPONIVEIS": 6000
    }
    
    # Configurações de preços padrão
    DEFAULT_PRICES = {
        "preco_soja": 2200,
        "preco_milho": 1300,
        "percentual_minimo_por_cultura": 0.15,
        "percentual_maximo_soja_produtiva": 0.60
    }
    
    def __new__(cls):
        """Implementa o padrão Singleton."""
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def get_scenario_manager(cls) -> ScenarioManager:
        """
        Retorna a instância única do ScenarioManager.
        
        Returns:
            Instância do ScenarioManager
        """
        if cls._scenario_manager is None:
            cls._scenario_manager = ScenarioManager(
                scenario_dir=str(cls.SCENARIO_DIR),
                base_name=cls.SCENARIO_BASE_NAME
            )
        return cls._scenario_manager
    
    @classmethod
    def get_default_scenario_template(cls) -> dict:
        """
        Retorna um template padrão para novos cenários.
        
        Returns:
            Dicionário com template de cenário
        """
        return {
            "# @package _group_": None,
            "params": cls.DEFAULT_PRICES.copy(),
            "resources": cls.DEFAULT_RESOURCES.copy(),
            "location": cls.DEFAULT_CLIMATE_CONFIG.copy()
        }
    
    @classmethod
    def ensure_directories(cls):
        """Garante que os diretórios necessários existem."""
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        cls.SCENARIO_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def get_app_config() -> AppConfig:
    """
    Retorna a instância única da configuração da aplicação.
    
    Returns:
        Instância do AppConfig
    """
    return AppConfig()


def get_scenario_manager() -> ScenarioManager:
    """
    Retorna a instância única do ScenarioManager.
    Função de conveniência para acesso rápido.
    
    Returns:
        Instância do ScenarioManager
    """
    return AppConfig.get_scenario_manager()
