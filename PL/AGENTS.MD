# AGENTS.MD

Este arquivo foi gerado automaticamente para ajudar agentes (humanos ou IA) a trabalhar com o projeto "Otimização do Mix de Culturas".

Resumo rápido
-------------
O ponto focal é o notebook `otimizacao_mix_culturas_v5_organized.ipynb` que contém funções reutilizáveis para gerar dados mock, configurar e resolver um modelo de otimização linear, e executar múltiplos cenários a partir de arquivos YAML.

Arquivos principais (caminhos relativos)
----------------------------------------
- Notebook principal: `otimizacao_mix_culturas_v5_organized.ipynb`
- Log principal (MASTER_LOG): `otimizacao_mix_culturas_v5_organized.txt` (criado/atualizado pelo notebook no mesmo diretório)
- Resumo de cenários gerado: `resumo_cenarios.csv` (gravado na raiz do notebook quando `run_all_scenarios` é executado)
- Diretório de cenários: `config/cenario/` (ex.: `config/cenario/base.yaml`, `config/cenario/agressivo.yaml`, etc.)
- Outros arquivos úteis no repositório: `README.md`, `requirements.txt`.

Funções-chave no notebook
-------------------------
- `print_and_log(message, logfile=MASTER_LOG)`
  - Loga mensagens no console e no arquivo `otimizacao_mix_culturas_v5_organized.txt` com timestamp.

- `generate_mock_data(n_dados=1500, seed=42, verbose=True)`
  - Gera um DataFrame com distribuições e parâmetros mock por cultura.

- `setup_model_from_params(params_df, resources, percentual_minimo_por_cultura=0.15, percentual_maximo_soja_produtiva=0.60)`
  - Constrói um modelo de otimização (pulp) a partir de parâmetros agregados por cultura e recursos disponíveis.
  - Retorna `(modelo, (x_sr, x_sp, x_ms))`.

- `run_optimization(cfg, logmaster=MASTER_LOG, verbose=True)`
  - Recebe um `cfg` (dict ou DictConfig) com `params` e `resources`, gera dados, agrega parâmetros, monta o modelo e resolve.
  - Retorna dict com chaves: `status`, `lucro`, `plantio`, `shadow_prices`.

- `load_and_merge_scenarios(scenario_dir='config/cenario', base_name='base')`
  - Carrega `base.yaml` e mescla com outros YAMLs em `config/cenario` retornando um dict de cenários.

- `run_all_scenarios(scenario_dir='config/cenario', base_name='base', save_csv='resumo_cenarios.csv', verbose=True)`
  - Executa `run_optimization` para cada cenário carregado e grava um resumo em CSV.

Artefatos gerados / esperados
------------------------------
- `otimizacao_mix_culturas_v5_organized.txt` — log contínuo com timestamps.
- `resumo_cenarios.csv` — tabela resumo com colunas: `cenario`, `status`, `lucro`, `plantio`.

Definição de sucesso / "resultado correto"
------------------------------------------
Ao rodar `run_all_scenarios`:
- Todos os YAMLs válidos em `config/cenario/` são processados.
- Para cada cenário `run_optimization` retorna um dicionário com `status == 'Optimal'`, `lucro` numérico e `plantio` com valores numéricos, quando possível.
- Invariante a checar: soma das áreas em `plantio` deve ser <= `AREA_TOTAL_DISPONIVEL_HA` do cenário (quando `status == 'Optimal'`).
- Os artefatos `otimizacao_mix_culturas_v5_organized.txt` e `resumo_cenarios.csv` devem existir e conter informação coerente.

Recomendações para organização e padrões
----------------------------------------
- Manter configs YAMLs em `config/cenario/` como feito hoje.
- Usar `print_and_log` para todo output relevante que agentes e pipelines possam ler.
- Seguir PEP8 e adicionar type hints nas funções principais (`generate_mock_data`, `setup_model_from_params`, `run_optimization`).
- Adicionar testes unitários simples (pytest) que validem:
  - `generate_mock_data` retorna um DataFrame com colunas esperadas;
  - `setup_model_from_params` cria um modelo sem erros para parâmetros mínimos;
  - `run_optimization` retorna chaves esperadas e respeita a invariant da área.

Passos rápidos para rodar (local)
---------------------------------
No diretório do notebook, com um ambiente Python que tenha as dependências do `requirements.txt`:
```bash
python -m pip install -r requirements.txt
# abrir jupyter ou executar partes do notebook via nbconvert ou papermill
jupyter notebook otimizacao_mix_culturas_v5_organized.ipynb
```

Testes e checagens automáticas sugeridas para a IA
--------------------------------------------------
- Após `modelo.solve()`, validar que `LpStatus[modelo.status] == 'Optimal'` antes de assumir valores; logar e salvar caso contrário.
- Validar soma das variáveis de plantio <= `AREA_TOTAL_DISPONIVEL_HA` (escrever aviso no log se violado).
- Garantir manipulação segura de arquivos (existência de `config/cenario` e `base.yaml`).

Como a IA pode ajudar com tarefas repetitivas
-------------------------------------------
- Executar `run_all_scenarios` automaticamente e coletar `resumo_cenarios.csv`.
- Verificar logs em `otimizacao_mix_culturas_v5_organized.txt` para detectar falhas repetidas e sugerir ajustes de parâmetros.
- Gerar PRs automatizados para adicionar type hints e testes mínimos.

Contato rápido
--------------
- Notebook: `otimizacao_mix_culturas_v5_organized.ipynb`
- Logs: `otimizacao_mix_culturas_v5_organized.txt`
- Cenários: `config/cenario/*.yaml`
- Resumo: `resumo_cenarios.csv`

---
Gerado automaticamente a partir do conteúdo presente em `otimizacao_mix_culturas_v5_organized.ipynb`.
