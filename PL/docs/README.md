# PL Organização Plantio

Este repositório contém otimizações para mix de culturas.

## Análise Climática (novo)

Um script auxiliar `analise_clima.py` foi adicionado para buscar dados climáticos históricos
usando a biblioteca `meteostat`. Ele resume precipitação por safra (Outubro-Março) e calcula
um fator simples de impacto na produtividade com base na precipitação observada.

Instalação das dependências:

```bash
pip install meteostat pandas
```

Exemplo de execução:

```bash
python analise_clima.py --lat -12.5449 --lon -55.7126 --years 2
```

O script gera um arquivo `resumo_precipitacao_safras.csv` com as safras processadas e suas
precipitações totais. Use o parâmetro `--media-historica` para alterar a referência de precipitação
quando necessário.

Cache (TinyDB)
----------------
Para evitar chamadas repetidas à API/classe de dados climáticos, o script suporta cache local
usando `TinyDB`. Quando disponível, os dados buscados são salvos em `cache_clima.json` com as
chaves: latitude, longitude, período (start/end). Antes de buscar novos dados, o script verifica
se existe um cache válido (por padrão 30 dias) e o reutiliza.

Instalação do TinyDB:

```bash
pip install tinydb
```

Parâmetros relacionados ao cache:
- `--estado` e `--cidade`: (opcionais) ajudam a identificar melhor a origem dos dados no cache.
- `--cache-days`: validade em dias do cache (default 30).

Redis (recomendado para ambientes com múltiplas execuções)
--------------------------------------------------------
O script agora suporta cache em Redis. Isso é útil quando você tem múltiplas execuções/serviços
que compartilham o mesmo cache ou quando quer persistência centralizada.

1) Subir o Redis com Docker Compose (no diretório do projeto):

```bash
docker compose up -d
```

2) Instalar cliente Python:

```bash
pip install redis
```

3) Executar o script apontando para o Redis (opcional):

```bash
python analise_clima.py --redis-url redis://localhost:6379/0 --lat -12.5449 --lon -55.7126
```

Se `--redis-url` não for informado, o script tentará se conectar em `redis://localhost:6379/0`.

Usando apenas um arquivo de configuração
---------------------------------------
Você pode simplificar a execução criando um arquivo JSON com os parâmetros e passando apenas
o nome do arquivo para o script. Exemplo de arquivo: `config_example.json` (fornecido).

Exemplo:

```bash
python analise_clima.py config_example.json
```

Você também pode copiar `.env.example` para `.env` e ajustar `REDIS_URL`/`CACHE_DAYS` para
evitar passar o `--redis-url` no CLI.


