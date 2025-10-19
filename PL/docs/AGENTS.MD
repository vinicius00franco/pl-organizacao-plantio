
# AGENTS.MD — Resumo simplificado

Este arquivo ajuda agentes (humanos ou IA) a entender rapidamente a organização do projeto e onde estão os artefatos principais.

Estrutura do projeto (resumida)
--------------------------------
Base do repositório (exemplo de saída do comando tree):

.
├── AGENTS.MD
├── config/cenario/ (YAMLs: `base.yaml`, `agressivo.yaml`, ...)
├── otimizacao_mix_culturas_v5_organized.ipynb
├── otimizacao_mix_culturas_v5_organized.txt  (log principal)
├── resumo_cenarios.csv  (resumo gerado por run_all_scenarios)
├── requirements.txt
└── vários notebooks de versões anteriores (v1..v4)

Arquivos e diretórios importantes
--------------------------------
- `otimizacao_mix_culturas_v5_organized.ipynb` — notebook principal organizado.
- `config/cenario/` — cenários em YAML usados por `run_all_scenarios`.
- `otimizacao_mix_culturas_v5_organized.txt` — arquivo de log central (MASTER_LOG).
- `resumo_cenarios.csv` — resumo em CSV com resultados por cenário.

O que o notebook faz (em poucas palavras)
-----------------------------------------
- Gera dados mock (`generate_mock_data`).
- Consolida parâmetros por cultura e calcula `lucro_ha` usando preços.
- Monta e resolve um modelo de programação linear (pulp) via `setup_model_from_params` e `run_optimization`.
- Executa múltiplos cenários carregados de `config/cenario` com `run_all_scenarios` e grava `resumo_cenarios.csv`.

Critérios mínimos de sucesso
----------------------------
- Para cada cenário esperado: `status == 'Optimal'`, `lucro` numérico e `plantio` (valores de hectares).
- Invariante importante: soma das hectares em `plantio` <= `AREA_TOTAL_DISPONIVEL_HA` do cenário.

Comandos rápidos
----------------
Instalar dependências e abrir o notebook:

```bash
python -m pip install -r requirements.txt
jupyter notebook otimizacao_mix_culturas_v5_organized.ipynb
```

Executar todos os cenários (dentro do notebook):

- Rodar a célula que chama `run_all_scenarios()` — ela grava `resumo_cenarios.csv` e escreve logs em `otimizacao_mix_culturas_v5_organized.txt`.

Observações para agentes/IA
--------------------------
- Sempre usar `print_and_log` para mensagens que devem ir para o log.
- Verificar `config/cenario/base.yaml` antes de rodar para garantir parâmetros padrão.
- Validar o `LpStatus` após `modelo.solve()` e registrar erros no log.

Se quiser, posso reduzir ainda mais este arquivo ou gerar um README curto com os mesmos pontos.
