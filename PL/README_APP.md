# 🌱 Sistema de Otimização de Plantio

Sistema completo de gestão, otimização e análise de cenários de plantio agrícola, com suporte a análise climática e visualização interativa.

## 📋 Funcionalidades

### 1. **Gerenciamento de Dados**
- Importação de dados reais via CSV
- Geração de dados simulados para testes
- Visualização estatística completa

### 2. **Gestão de Cenários**
- Visualização de todos os cenários disponíveis
- Edição de cenários existentes
- Criação de novos cenários
- Sistema baseado em YAML com herança de configuração base

### 3. **Análise Climática**
- Consulta por cidade (cidades do MT, GO, MS, PI, BA pré-cadastradas)
- Consulta por coordenadas GPS (lat/lon)
- Comparação entre múltiplas localizações
- Dados históricos via Meteostat
- Cache Redis opcional para performance

### 4. **Otimização**
- Modelo de programação linear (PuLP)
- Maximização de lucro com restrições de recursos
- Diversificação de culturas (gestão de risco)
- Execução de múltiplos cenários em batch
- Integração com dados climáticos

### 5. **Relatórios e Análises**
- Comparação visual entre cenários
- Análise de preços sombra (dual prices)
- Identificação de gargalos de recursos
- Gráficos interativos (Plotly)
- Exportação de resultados em CSV

## 🚀 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip

### Passos

1. **Clone o repositório** (ou navegue até a pasta do projeto)

```bash
cd /home/vinicius/Downloads/estudo/po/PL/PL
```

2. **Crie um ambiente virtual** (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **(Opcional) Configure Redis para cache climático**

Se você tem Redis instalado, crie um arquivo `.env` na raiz:

```env
REDIS_URL=redis://localhost:6379/0
CACHE_DAYS=30
```

## 📖 Como Usar

### Iniciar a Aplicação

```bash
streamlit run src/app.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

### Workflow Recomendado

1. **📊 Dados da Fazenda**
   - Importe um CSV com dados reais OU
   - Gere dados simulados para teste

2. **🎯 Cenários**
   - Explore os cenários existentes (base, agressivo, conservador, seca, etc.)
   - Edite parâmetros (preços, restrições, localização)
   - Crie novos cenários conforme necessário

3. **🌤️ Análise Climática**
   - Consulte dados climáticos da sua região
   - Compare diferentes localizações
   - Entenda o fator de impacto climático

4. **🚀 Otimização**
   - Selecione cenários para executar
   - Visualize os planos de plantio recomendados
   - Execute com ou sem ajuste climático

5. **📈 Relatórios**
   - Compare resultados entre cenários
   - Identifique gargalos críticos
   - Priorize investimentos em recursos
   - Baixe planilhas detalhadas

## 📁 Estrutura do Projeto

```
PL/
├── config/
│   └── cenario/          # Arquivos YAML de cenários
│       ├── base.yaml
│       ├── agressivo.yaml
│       ├── conservador.yaml
│       └── ...
├── scripts/
│   └── analise_clima.py  # Script de análise climática
├── src/
│   ├── models/
│   │   └── otimizacao.py # Modelo de otimização
│   ├── services/
│   │   ├── scenario_manager.py   # Gerenciador de cenários
│   │   └── climate_service.py    # Serviço climático
│   ├── pages/
│   │   ├── 01_dados_fazenda.py
│   │   ├── 02_cenarios.py
│   │   ├── 03_analise_clima.py
│   │   ├── 04_otimizacao.py
│   │   └── 05_relatorios.py
│   └── app.py            # Aplicação principal
├── notebooks/            # Notebooks Jupyter (desenvolvimento)
├── requirements.txt
└── README.md
```

## 🎯 Cenários Incluídos

- **base**: Configuração padrão balanceada
- **agressivo**: Maior percentual de soja produtiva (maior risco/retorno)
- **conservador**: Menor percentual de soja produtiva (menor risco)
- **seca**: Restrição de água reduzida
- **preco_alto_soja**: Preço de soja elevado
- **crise_fertilizantes**: Redução de 30% em potássio e fósforo

## 🔧 Configuração de Cenários

### Formato YAML

```yaml
# @package _group_

params:
  preco_soja: 2200          # R$/tonelada
  preco_milho: 1300         # R$/tonelada
  percentual_minimo_por_cultura: 0.15     # 15% mínimo cada cultura
  percentual_maximo_soja_produtiva: 0.60  # 60% máximo soja produtiva

resources:
  AREA_TOTAL_DISPONIVEL_HA: 500
  ORCAMENTO_TOTAL_DISPONIVEL: 1100000
  AGUA_TOTAL_DISPONIVEL_M3: 250000
  POTASSIO_DISPONIVEL_KG: 45000
  FOSFORO_DISPONIVEL_KG: 42000

location:
  lat: -12.5449      # Sorriso, MT
  lon: -55.7126
  years: 2           # Anos de histórico climático
  media_historica: 600.0  # mm de precipitação
```

## 📊 Formato CSV de Dados

```csv
id_talhao,cultura,produtividade_ton_ha,custo_ha,uso_agua_m3_ha,demanda_k_kg_ha,demanda_p_kg_ha,horas_maquina_ha
1,Soja_Resistente,3.5,1800,450,80,70,10
2,Soja_Produtiva,4.8,2500,600,100,90,12
3,Milho_Safrinha,5.5,2800,700,120,100,15
...
```

## 🤝 Contribuindo

1. Crie novos cenários em `config/cenario/`
2. Adicione novas cidades em `src/services/climate_service.py` (CIDADES_OUTRAS)
3. Customize parâmetros das culturas em `src/models/otimizacao.py`

## 📝 Notas Técnicas

- **Solver**: CBC (via PuLP) - solver open-source para programação linear
- **Dados Climáticos**: Meteostat API (dados históricos globais)
- **Cache**: Redis opcional para acelerar consultas climáticas repetidas
- **Frontend**: Streamlit (interface web reativa)

## 🐛 Troubleshooting

### Erro ao importar streamlit
```bash
pip install --upgrade streamlit
```

### Erro de solver (PuLP)
```bash
pip install pulp
# Certifique-se que o CBC solver está disponível
```

### Dados climáticos indisponíveis
- Verifique sua conexão com a internet
- Tente coordenadas diferentes (algumas regiões têm cobertura limitada)
- Reduza o número de anos de histórico

## 📄 Licença

Este projeto é de código aberto para uso educacional e comercial.

## 👥 Autores

Sistema desenvolvido para otimização de mix de culturas agrícolas.

---

**Versão**: 1.0.0  
**Última atualização**: Outubro 2025
