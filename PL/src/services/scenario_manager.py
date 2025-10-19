"""
Serviço de gerenciamento de cenários YAML.
Permite carregar, editar, salvar e criar novos cenários.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from omegaconf import DictConfig, OmegaConf
import yaml


class ScenarioManager:
    """Gerenciador de cenários de otimização."""
    
    def __init__(self, scenario_dir: str = "config/cenario", base_name: str = "base"):
        """
        Inicializa o gerenciador de cenários.
        
        Args:
            scenario_dir: Diretório contendo os arquivos YAML
            base_name: Nome do arquivo base (sem extensão)
        """
        self.scenario_dir = Path(scenario_dir)
        self.base_name = base_name
        self.base_path = self.scenario_dir / f"{base_name}.yaml"
        
    def load_base_config(self) -> DictConfig:
        """Carrega a configuração base."""
        if not self.base_path.exists():
            raise FileNotFoundError(f"Arquivo base não encontrado: {self.base_path}")
        return OmegaConf.load(self.base_path)
    
    def list_scenarios(self) -> List[str]:
        """Lista todos os cenários disponíveis."""
        if not self.scenario_dir.exists():
            return []
        
        scenarios = []
        for file in self.scenario_dir.glob("*.yaml"):
            if file.stem != self.base_name:
                scenarios.append(file.stem)
        
        return sorted([self.base_name] + scenarios)
    
    def load_scenario(self, scenario_name: str) -> DictConfig:
        """
        Carrega um cenário específico (mergeado com base).
        
        Args:
            scenario_name: Nome do cenário
        
        Returns:
            Configuração mergeada
        """
        base_cfg = self.load_base_config()
        
        if scenario_name == self.base_name:
            return base_cfg
        
        scenario_path = self.scenario_dir / f"{scenario_name}.yaml"
        if not scenario_path.exists():
            raise FileNotFoundError(f"Cenário não encontrado: {scenario_path}")
        
        scenario_cfg = OmegaConf.load(scenario_path)
        return OmegaConf.merge(base_cfg.copy(), scenario_cfg)
    
    def load_all_scenarios(self) -> Dict[str, DictConfig]:
        """
        Carrega todos os cenários disponíveis.
        
        Returns:
            Dicionário {nome_cenario: configuração}
        """
        scenarios = {}
        for name in self.list_scenarios():
            try:
                scenarios[name] = self.load_scenario(name)
            except Exception as e:
                print(f"Erro ao carregar cenário {name}: {e}")
        
        return scenarios
    
    def get_scenario_diff(self, scenario_name: str) -> Dict[str, Any]:
        """
        Retorna apenas as diferenças em relação à base.
        
        Args:
            scenario_name: Nome do cenário
        
        Returns:
            Dicionário com diferenças
        """
        if scenario_name == self.base_name:
            return OmegaConf.to_container(self.load_base_config(), resolve=True)
        
        scenario_path = self.scenario_dir / f"{scenario_name}.yaml"
        if not scenario_path.exists():
            return {}
        
        scenario_cfg = OmegaConf.load(scenario_path)
        return OmegaConf.to_container(scenario_cfg, resolve=True)
    
    def save_scenario(self, scenario_name: str, config: Dict[str, Any], overwrite: bool = False):
        """
        Salva um cenário (apenas diferenças em relação à base).
        
        Args:
            scenario_name: Nome do cenário
            config: Configuração completa ou diferencial
            overwrite: Se True, sobrescreve arquivo existente
        """
        scenario_path = self.scenario_dir / f"{scenario_name}.yaml"
        
        if scenario_path.exists() and not overwrite:
            raise FileExistsError(f"Cenário já existe: {scenario_name}. Use overwrite=True para sobrescrever.")
        
        # Cria diretório se não existir
        self.scenario_dir.mkdir(parents=True, exist_ok=True)
        
        # Salva configuração
        with open(scenario_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    def delete_scenario(self, scenario_name: str):
        """
        Remove um cenário.
        
        Args:
            scenario_name: Nome do cenário
        """
        if scenario_name == self.base_name:
            raise ValueError("Não é possível deletar o cenário base")
        
        scenario_path = self.scenario_dir / f"{scenario_name}.yaml"
        if scenario_path.exists():
            scenario_path.unlink()
        else:
            raise FileNotFoundError(f"Cenário não encontrado: {scenario_name}")
    
    def create_scenario_template(self, scenario_name: str, description: str = "") -> Dict[str, Any]:
        """
        Cria um template para novo cenário.
        
        Args:
            scenario_name: Nome do novo cenário
            description: Descrição do cenário
        
        Returns:
            Template de cenário
        """
        return {
            "# @package _group_": None,
            "_description": description or f"Cenário {scenario_name}",
            "params": {
                "preco_soja": 2200,
                "preco_milho": 1300,
            },
            "resources": {},
            "location": {
                "lat": -12.5449,
                "lon": -55.7126,
                "years": 2,
                "media_historica": 600.0
            }
        }
    
    def get_scenario_summary(self, scenario_name: str) -> Dict[str, Any]:
        """
        Retorna um resumo do cenário.
        
        Args:
            scenario_name: Nome do cenário
        
        Returns:
            Resumo com informações principais
        """
        try:
            cfg = self.load_scenario(scenario_name)
            cfg_dict = OmegaConf.to_container(cfg, resolve=True)
            
            params = cfg_dict.get('params', {})
            resources = cfg_dict.get('resources', {})
            location = cfg_dict.get('location', {})
            
            return {
                'nome': scenario_name,
                'preco_soja': params.get('preco_soja'),
                'preco_milho': params.get('preco_milho'),
                'area_total': resources.get('AREA_TOTAL_DISPONIVEL_HA'),
                'orcamento': resources.get('ORCAMENTO_TOTAL_DISPONIVEL'),
                'agua_disponivel': resources.get('AGUA_TOTAL_DISPONIVEL_M3'),
                'localizacao': f"Lat {location.get('lat', 'N/A')}, Lon {location.get('lon', 'N/A')}" if location else "N/A"
            }
        except Exception as e:
            return {'nome': scenario_name, 'erro': str(e)}
