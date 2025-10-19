#!/usr/bin/env python3
"""
analise_clima.py

Busca dados climáticos históricos usando Meteostat e calcula um fator de impacto
na produtividade baseado na precipitação durante a safra de soja.

Uso:
    python analise_clima.py --lat -12.5449 --lon -55.7126 --years 2

Parâmetros principais:
    --lat, --lon: coordenadas da propriedade (padrão: Sorriso, MT exemplo)
    --years: quantos anos retroativos buscar (padrão: 2)

Dependências:
    pip install meteostat pandas
"""

from datetime import datetime, timedelta
import argparse
import sys

import pandas as pd

try:
    from meteostat import Point, Daily
except Exception as e:
    print("Erro ao importar 'meteostat'. Instale com: pip install meteostat")
    raise

try:
    import redis
    import json
except Exception:
    print("Aviso: redis (redis-py) não encontrado. Instale com: pip install redis")
    redis = None
    json = None


def parse_args():
    parser = argparse.ArgumentParser(
        description="Análise climática para impactar produtividade"
    )
    parser.add_argument(
        "config_file",
        nargs="?",
        default=None,
        help="Arquivo JSON de configuração com parâmetros (opcional). Se fornecido, sobrepõe outras flags.",
    )
    parser.add_argument(
        "--lat", type=float, default=-12.5449, help="Latitude da propriedade"
    )
    parser.add_argument(
        "--lon", type=float, default=-55.7126, help="Longitude da propriedade"
    )
    parser.add_argument(
        "--years", type=int, default=2, help="Número de anos retroativos a buscar"
    )
    parser.add_argument(
        "--estado", type=str, default=None, help="Estado/UF da propriedade (opcional)"
    )
    parser.add_argument(
        "--cidade",
        type=str,
        default=None,
        help="Cidade/município da propriedade (opcional)",
    )
    parser.add_argument(
        "--media-historica",
        type=float,
        default=600.0,
        help="Média histórica de precipitação na safra (mm) para referência",
    )
    parser.add_argument(
        "--cache-days",
        type=int,
        default=None,
        help="Validade do cache em dias (padrão 30 ou variável de ambiente CACHE_DAYS)",
    )
    parser.add_argument(
        "--redis-url",
        type=str,
        default=None,
        help="URL do Redis, ex: redis://localhost:6379/0 (pode ser definido em REDIS_URL no .env)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    cfg = load_config(args)

    # Conectar Redis (se possível)
    r = connect_redis(cfg.get("redis_url"))

    # Determina intervalo
    end = datetime.now()
    start = datetime(end.year - cfg.get("years"), end.month, end.day)

    # Tenta obter dados do cache ou buscar
    data = get_cached_or_fetch(r, cfg, start, end)

    if data is None or data.empty:
        print("Nenhum dado climático encontrado para a localização e período.")
        sys.exit(0)

    # Processamento e saída
    precipitacoes = calc_safra_precip(data, start, end)
    print("\n--- Análise de Precipitação (Safra Soja) ---")
    for s, e, pr in precipitacoes:
        if pd.isna(pr):
            print(f"Safra ({s} a {e}): dados insuficientes")
        else:
            print(f"Precipitação Safra ({s} a {e}): {pr:.2f} mm")

    print(f"Média histórica de referência: {cfg.get('media_historica')} mm")

    if not pd.isna(precipitacoes[-1][2]):
        precipitacao_safra_mais_recente = precipitacoes[-1][2]
        fator_impacto = calc_fator_impacto(
            precipitacao_safra_mais_recente, cfg.get("media_historica")
        )
        print(
            f"\nFator de Impacto para a produtividade da próxima safra: {fator_impacto:.2f}"
        )
    else:
        print(
            "Não foi possível calcular fator de impacto por falta de dados na safra mais recente."
        )

    resumo_path = "resumo_precipitacao_safras.csv"
    save_resumo(precipitacoes, resumo_path)
    print(f"Resumo salvo em: {resumo_path}")


def load_config(args):
    """Carrega parâmetros a partir de args, config file e .env (se disponível)."""
    # carrega .env se disponível
    try:
        from dotenv import load_dotenv
        import os

        load_dotenv()
    except Exception:
        os = None

    # valores base
    cfg = {
        "lat": args.lat,
        "lon": args.lon,
        "years": args.years,
        "estado": args.estado,
        "cidade": args.cidade,
        "media_historica": args.media_historica,
        "cache_days": args.cache_days if args.cache_days is not None else None,
        "redis_url": args.redis_url,
    }

    # carrega arquivo JSON se fornecido
    import json as _json

    if args.config_file:
        try:
            with open(args.config_file, "r", encoding="utf-8") as f:
                file_cfg = _json.load(f)
            cfg.update({k: file_cfg.get(k, v) for k, v in cfg.items()})
        except Exception as e:
            print(f"Aviso: falha ao carregar config file {args.config_file}: {e}")

    # valores por ambiente
    try:
        if cfg.get("cache_days") is None:
            if os is not None and os.getenv("CACHE_DAYS"):
                cfg["cache_days"] = int(os.getenv("CACHE_DAYS"))
            else:
                cfg["cache_days"] = 30
    except Exception:
        cfg["cache_days"] = 30

    try:
        if cfg.get("redis_url") is None and os is not None and os.getenv("REDIS_URL"):
            cfg["redis_url"] = os.getenv("REDIS_URL")
    except Exception:
        cfg["redis_url"] = None

    return cfg


def connect_redis(redis_url):
    """Tenta conectar ao Redis; retorna cliente ou None."""
    if redis is None:
        return None
    try:
        url = redis_url or "redis://localhost:6379/0"
        return redis.from_url(url)
    except Exception as e:
        print(f"Aviso: falha ao conectar Redis: {e}")
        return None


def get_cached_or_fetch(r, cfg, start, end):
    """Tenta obter dados do cache Redis; se ausente, busca do Meteostat e salva no Redis."""
    propriedade_location = Point(cfg.get("lat"), cfg.get("lon"))

    cache_key_parts = [
        f"lat:{round(cfg.get('lat'),5)}",
        f"lon:{round(cfg.get('lon'),5)}",
        f"start:{start.strftime('%Y-%m-%d')}",
        f"end:{end.strftime('%Y-%m-%d')}",
    ]
    if cfg.get("estado"):
        cache_key_parts.append(f"estado:{cfg.get('estado').lower()}")
    if cfg.get("cidade"):
        cache_key_parts.append(f"cidade:{cfg.get('cidade').lower()}")

    cache_key = "clima:" + ":".join(cache_key_parts)

    if r is not None:
        raw = r.get(cache_key)
        if raw:
            try:
                payload = json.loads(raw)
                fetched_at = datetime.fromisoformat(payload.get("fetched_at"))
                if datetime.now() - fetched_at <= timedelta(days=cfg.get("cache_days")):
                    print("Usando dados do cache Redis")
                    cached_df = pd.read_json(payload["data"], convert_dates=True)
                    cached_df.index = pd.to_datetime(cached_df.index)
                    return cached_df
            except Exception:
                pass

    # se não havia cache válido, buscar
    print(
        f"Buscando dados climáticos para Lat={cfg.get('lat')}, Lon={cfg.get('lon')} de {start.date()} a {end.date()}..."
    )
    try:
        data = Daily(propriedade_location, start, end)
        data = data.fetch()
    except Exception as e:
        print(f"Falha ao buscar dados meteorológicos: {e}")
        return None

    if r is not None:
        try:
            payload = {
                "fetched_at": datetime.now().isoformat(),
                "data": data.to_json(date_format="iso"),
            }
            ttl_seconds = cfg.get("cache_days") * 24 * 3600
            r.set(cache_key, json.dumps(payload), ex=ttl_seconds)
            print("Dados salvos no cache Redis")
        except Exception as e:
            print(f"Aviso: falha ao salvar cache no Redis: {e}")

    return data
    # --- BLOCO LEGADO / DUPLICADO ---
    # O trecho a seguir é a versão antiga da lógica de cache/busca que foi
    # mantida no repositório durante refactor. Ele está comentado para evitar
    # execução dupla, mas preservado aqui como referência durante a migração
    # para Redis e para facilitar futuras inspeções. Não é executado porque
    # está abaixo do `return data` acima.
    #
    # lat = args.lat
    # lon = args.lon
    # years = args.years
    # media_historica_mm = args.media_historica
    #
    # propriedade_location = Point(lat, lon)
    #
    # end = datetime.now()
    # # start retroativo `years` anos completos desde a data atual
    # start = datetime(end.year - years, end.month, end.day)
    #
    # # Verifica cache Redis antes de fazer chamada externa
    # cache_key_parts = [
    #     f"lat:{round(lat,5)}",
    #     f"lon:{round(lon,5)}",
    #     f"start:{start.strftime('%Y-%m-%d')}",
    #     f"end:{end.strftime('%Y-%m-%d')}",
    # ]
    # if args.estado:
    #     cache_key_parts.append(f"estado:{args.estado.lower()}")
    # if args.cidade:
    #     cache_key_parts.append(f"cidade:{args.cidade.lower()}")
    #
    # cache_key = "clima:" + ":".join(cache_key_parts)
    #
    # cached_data = None
    # r = None
    # if redis is not None:
    #     try:
    #         redis_url = args.redis_url or "redis://localhost:6379/0"
    #         r = redis.from_url(redis_url)
    #         raw = r.get(cache_key)
    #         if raw:
    #             try:
    #                 payload = json.loads(raw)
    #                 fetched_at = datetime.fromisoformat(payload.get("fetched_at"))
    #                 if datetime.now() - fetched_at <= timedelta(days=args.cache_days):
    #                     print("Usando dados do cache Redis")
    #                     cached_df = pd.read_json(payload["data"], convert_dates=True)
    #                     cached_df.index = pd.to_datetime(cached_df.index)
    #                     cached_data = cached_df
    #             except Exception:
    #                 # se parsing falhar, ignorar cache
    #                 cached_data = None
    #     except Exception as e:
    #         print(f"Aviso: falha ao conectar/usar Redis: {e}")
    #
    # if cached_data is not None:
    #     data = cached_data
    # else:
    #     print(
    #         f"Buscando dados climáticos para Lat={lat}, Lon={lon} de {start.date()} a {end.date()}..."
    #     )
    #     try:
    #         data = Daily(propriedade_location, start, end)
    #         data = data.fetch()
    #     except Exception as e:
    #         print(f"Falha ao buscar dados meteorológicos: {e}")
    #         sys.exit(1)
    #
    #     # salvar no cache Redis se conectado
    #     if r is not None:
    #         try:
    #             payload = {
    #                 "fetched_at": datetime.now().isoformat(),
    #                 "data": data.to_json(date_format="iso"),
    #             }
    #             # salvar com TTL (cache_days)
    #             ttl_seconds = args.cache_days * 24 * 3600
    #             r.set(cache_key, json.dumps(payload), ex=ttl_seconds)
    #             print("Dados salvos no cache Redis")
    #         except Exception as e:
    #             print(f"Aviso: falha ao salvar cache no Redis: {e}")
    #
    # # Garante que colunas esperadas existam
    # if "prcp" not in data.columns:
    #     print("Dados retornados não contêm a coluna 'prcp' (precipitação).")
    #     sys.exit(1)


def calc_safra_precip(data, start, end):
    """Calcula precipitação por janelas de safra (Outubro-Março) dentro do período start..end.
    Retorna lista de tuplas (start, end, precipitacao_mm) para as últimas duas safras encontradas.
    """
    safra_windows = []
    for y in range(start.year, end.year + 1):
        s = f"{y}-10-01"
        e = f"{y+1}-03-31"
        safra_windows.append((s, e))

    precipitacoes = []
    for s, e in safra_windows[-2:]:
        try:
            pr = data.prcp.loc[s:e].sum()
        except Exception:
            pr = float("nan")
        precipitacoes.append((s, e, pr))

    return precipitacoes


def calc_fator_impacto(precipitacao, media_historica_mm):
    """Calcula um fator de impacto simples na produtividade com base na precipitação observada."""
    return 1 + ((precipitacao - media_historica_mm) / media_historica_mm) * 0.8


def save_resumo(precipitacoes, path):
    resumo = pd.DataFrame(precipitacoes, columns=["start", "end", "precipitacao_mm"])
    resumo.to_csv(path, index=False)


if __name__ == "__main__":
    main()


# API programática para uso em notebooks
def fetch_climate(cfg):
    """
    Busca/clona dados climáticos para uso programático.

    Parâmetros esperados em `cfg` (dict-like):
      - lat, lon, years, media_historica, cache_days, redis_url

    Retorna dict com chaves:
      - data: DataFrame (ou None)
      - precipitacoes: lista de tuplas (start, end, precip) ou None
      - fator: float ou None
    """
    # valores defaults seguros
    lat = cfg.get("lat", -12.5449)
    lon = cfg.get("lon", -55.7126)
    years = int(cfg.get("years", 2))
    media_hist = float(cfg.get("media_historica", 600.0))
    cache_days = int(cfg.get("cache_days", 30)) if cfg.get("cache_days") is not None else 30
    redis_url = cfg.get("redis_url")

    # prepara cfg simplificado para reusar funções internas
    local_cfg = {
        "lat": lat,
        "lon": lon,
        "years": years,
        "media_historica": media_hist,
        "cache_days": cache_days,
        "redis_url": redis_url,
    }

    r = connect_redis(redis_url)
    end = datetime.now()
    start = datetime(end.year - years, end.month, end.day)

    data = get_cached_or_fetch(r, local_cfg, start, end)
    if data is None or (hasattr(data, 'empty') and data.empty):
        return {"data": None, "precipitacoes": None, "fator": None}

    precipitacoes = calc_safra_precip(data, start, end)
    fator = None
    try:
        ultima = precipitacoes[-1][2]
        if not pd.isna(ultima):
            fator = calc_fator_impacto(ultima, media_hist)
    except Exception:
        fator = None

    return {"data": data, "precipitacoes": precipitacoes, "fator": fator}
