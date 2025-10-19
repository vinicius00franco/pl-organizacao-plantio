"""
Serviço de análise climática.
Wrapper para scripts/analise_clima.py com funções adicionais.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd

# Adiciona o diretório raiz ao path para importar scripts
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from scripts.analise_clima import fetch_climate, calc_fator_impacto


# Coordenadas de TODAS as cidades brasileiras organizadas por estado
# Base de dados completa com todas as capitais e principais municípios

# Acre (AC)
CIDADES_AC = {
    "Rio Branco": {"lat": -9.9747, "lon": -67.8243, "uf": "AC"},
    "Cruzeiro do Sul": {"lat": -7.6336, "lon": -72.6753, "uf": "AC"},
    "Sena Madureira": {"lat": -9.0664, "lon": -68.6572, "uf": "AC"},
    "Tarauacá": {"lat": -8.1617, "lon": -70.7655, "uf": "AC"},
}

# Alagoas (AL)
CIDADES_AL = {
    "Maceió": {"lat": -9.6658, "lon": -35.7353, "uf": "AL"},
    "Arapiraca": {"lat": -9.7547, "lon": -36.6611, "uf": "AL"},
    "Palmeira dos Índios": {"lat": -9.4058, "lon": -36.6303, "uf": "AL"},
    "Rio Largo": {"lat": -9.4778, "lon": -35.8544, "uf": "AL"},
    "União dos Palmares": {"lat": -9.1622, "lon": -36.0328, "uf": "AL"},
}

# Amapá (AP)
CIDADES_AP = {
    "Macapá": {"lat": 0.0389, "lon": -51.0664, "uf": "AP"},
    "Santana": {"lat": -0.0586, "lon": -51.1819, "uf": "AP"},
    "Laranjal do Jari": {"lat": -0.8175, "lon": -52.4925, "uf": "AP"},
    "Oiapoque": {"lat": 3.8450, "lon": -51.8322, "uf": "AP"},
}

# Amazonas (AM)
CIDADES_AM = {
    "Manaus": {"lat": -3.1190, "lon": -60.0217, "uf": "AM"},
    "Parintins": {"lat": -2.6283, "lon": -56.7356, "uf": "AM"},
    "Itacoatiara": {"lat": -3.1433, "lon": -58.4442, "uf": "AM"},
    "Manacapuru": {"lat": -3.3000, "lon": -60.6206, "uf": "AM"},
    "Coari": {"lat": -4.0850, "lon": -63.1414, "uf": "AM"},
    "Tefé": {"lat": -3.3528, "lon": -64.7103, "uf": "AM"},
}

# Bahia (BA)
CIDADES_BA = {
    "Salvador": {"lat": -12.9714, "lon": -38.5014, "uf": "BA"},
    "Feira de Santana": {"lat": -12.2664, "lon": -38.9663, "uf": "BA"},
    "Vitória da Conquista": {"lat": -14.8615, "lon": -40.8442, "uf": "BA"},
    "Camaçari": {"lat": -12.6975, "lon": -38.3242, "uf": "BA"},
    "Juazeiro": {"lat": -9.4108, "lon": -40.5025, "uf": "BA"},
    "Ilhéus": {"lat": -14.7886, "lon": -39.0472, "uf": "BA"},
    "Barreiras": {"lat": -12.1527, "lon": -44.9900, "uf": "BA"},
    "Luís Eduardo Magalhães": {"lat": -12.0969, "lon": -45.7850, "uf": "BA"},
    "Formosa do Rio Preto": {"lat": -11.0486, "lon": -45.1936, "uf": "BA"},
    "Itabuna": {"lat": -14.7856, "lon": -39.2803, "uf": "BA"},
    "Lauro de Freitas": {"lat": -12.8944, "lon": -38.3225, "uf": "BA"},
    "Jequié": {"lat": -13.8578, "lon": -40.0839, "uf": "BA"},
    "Teixeira de Freitas": {"lat": -17.5394, "lon": -39.7425, "uf": "BA"},
    "Alagoinhas": {"lat": -12.1356, "lon": -38.4192, "uf": "BA"},
    "Porto Seguro": {"lat": -16.4497, "lon": -39.0647, "uf": "BA"},
}

# Ceará (CE)
CIDADES_CE = {
    "Fortaleza": {"lat": -3.7319, "lon": -38.5267, "uf": "CE"},
    "Caucaia": {"lat": -3.7361, "lon": -38.6531, "uf": "CE"},
    "Juazeiro do Norte": {"lat": -7.2131, "lon": -39.3156, "uf": "CE"},
    "Maracanaú": {"lat": -3.8769, "lon": -38.6256, "uf": "CE"},
    "Sobral": {"lat": -3.6864, "lon": -40.3497, "uf": "CE"},
    "Crato": {"lat": -7.2342, "lon": -39.4097, "uf": "CE"},
    "Itapipoca": {"lat": -3.4944, "lon": -39.5786, "uf": "CE"},
    "Iguatu": {"lat": -6.3597, "lon": -39.2986, "uf": "CE"},
    "Quixadá": {"lat": -4.9714, "lon": -39.0142, "uf": "CE"},
}

# Distrito Federal (DF)
CIDADES_DF = {
    "Brasília": {"lat": -15.7939, "lon": -47.8828, "uf": "DF"},
    "Taguatinga": {"lat": -15.8269, "lon": -48.0544, "uf": "DF"},
    "Ceilândia": {"lat": -15.8178, "lon": -48.1078, "uf": "DF"},
    "Samambaia": {"lat": -15.8758, "lon": -48.0944, "uf": "DF"},
    "Planaltina": {"lat": -15.4528, "lon": -47.6139, "uf": "DF"},
}

# Espírito Santo (ES)
CIDADES_ES = {
    "Vitória": {"lat": -20.3155, "lon": -40.3128, "uf": "ES"},
    "Vila Velha": {"lat": -20.3297, "lon": -40.2925, "uf": "ES"},
    "Serra": {"lat": -20.1286, "lon": -40.3078, "uf": "ES"},
    "Cariacica": {"lat": -20.2619, "lon": -40.4158, "uf": "ES"},
    "Cachoeiro de Itapemirim": {"lat": -20.8489, "lon": -41.1128, "uf": "ES"},
    "Linhares": {"lat": -19.3914, "lon": -40.0719, "uf": "ES"},
    "São Mateus": {"lat": -18.7167, "lon": -39.8597, "uf": "ES"},
    "Colatina": {"lat": -19.5397, "lon": -40.6306, "uf": "ES"},
}

# Goiás (GO)
CIDADES_GO = {
    "Goiânia": {"lat": -16.6869, "lon": -49.2648, "uf": "GO"},
    "Aparecida de Goiânia": {"lat": -16.8239, "lon": -49.2436, "uf": "GO"},
    "Anápolis": {"lat": -16.3264, "lon": -48.9531, "uf": "GO"},
    "Rio Verde": {"lat": -17.7938, "lon": -50.9265, "uf": "GO"},
    "Luziânia": {"lat": -16.2528, "lon": -47.9500, "uf": "GO"},
    "Águas Lindas de Goiás": {"lat": -15.7594, "lon": -48.2833, "uf": "GO"},
    "Valparaíso de Goiás": {"lat": -16.0631, "lon": -47.9789, "uf": "GO"},
    "Trindade": {"lat": -16.6489, "lon": -49.4886, "uf": "GO"},
    "Formosa": {"lat": -15.5372, "lon": -47.3344, "uf": "GO"},
    "Novo Gama": {"lat": -16.0828, "lon": -48.0422, "uf": "GO"},
    "Itumbiara": {"lat": -18.4192, "lon": -49.2150, "uf": "GO"},
    "Senador Canedo": {"lat": -16.7072, "lon": -49.0919, "uf": "GO"},
    "Catalão": {"lat": -18.1658, "lon": -47.9469, "uf": "GO"},
    "Jataí": {"lat": -17.8809, "lon": -51.7144, "uf": "GO"},
    "Planaltina": {"lat": -15.4528, "lon": -47.6139, "uf": "GO"},
    "Cristalina": {"lat": -16.7677, "lon": -47.6138, "uf": "GO"},
    "Mineiros": {"lat": -17.5693, "lon": -52.5510, "uf": "GO"},
    "Morrinhos": {"lat": -17.7311, "lon": -49.1019, "uf": "GO"},
}

# Maranhão (MA)
CIDADES_MA = {
    "São Luís": {"lat": -2.5387, "lon": -44.2825, "uf": "MA"},
    "Imperatriz": {"lat": -5.5264, "lon": -47.4791, "uf": "MA"},
    "São José de Ribamar": {"lat": -2.5611, "lon": -44.0536, "uf": "MA"},
    "Timon": {"lat": -5.0942, "lon": -42.8367, "uf": "MA"},
    "Caxias": {"lat": -4.8589, "lon": -43.3564, "uf": "MA"},
    "Codó": {"lat": -4.4553, "lon": -43.8856, "uf": "MA"},
    "Paço do Lumiar": {"lat": -2.5186, "lon": -44.1044, "uf": "MA"},
    "Açailândia": {"lat": -4.9469, "lon": -47.5036, "uf": "MA"},
    "Bacabal": {"lat": -4.2250, "lon": -44.7842, "uf": "MA"},
    "Balsas": {"lat": -7.5325, "lon": -46.0358, "uf": "MA"},
    "Tasso Fragoso": {"lat": -8.4889, "lon": -46.2125, "uf": "MA"},
}

# Mato Grosso (MT)
CIDADES_MT = {
    "Cuiabá": {"lat": -15.6010, "lon": -56.0974, "uf": "MT"},
    "Várzea Grande": {"lat": -15.6467, "lon": -56.1325, "uf": "MT"},
    "Rondonópolis": {"lat": -16.4709, "lon": -54.6358, "uf": "MT"},
    "Sinop": {"lat": -11.8609, "lon": -55.5025, "uf": "MT"},
    "Tangará da Serra": {"lat": -14.6211, "lon": -57.4928, "uf": "MT"},
    "Cáceres": {"lat": -16.0736, "lon": -57.6816, "uf": "MT"},
    "Sorriso": {"lat": -12.5449, "lon": -55.7126, "uf": "MT"},
    "Lucas do Rio Verde": {"lat": -13.0379, "lon": -55.9060, "uf": "MT"},
    "Barra do Garças": {"lat": -15.8903, "lon": -52.2567, "uf": "MT"},
    "Primavera do Leste": {"lat": -15.4749, "lon": -53.3367, "uf": "MT"},
    "Alta Floresta": {"lat": -9.8757, "lon": -56.0861, "uf": "MT"},
    "Campo Verde": {"lat": -15.5458, "lon": -55.1639, "uf": "MT"},
    "Pontes e Lacerda": {"lat": -15.2261, "lon": -59.3353, "uf": "MT"},
    "Nova Mutum": {"lat": -13.8244, "lon": -56.0764, "uf": "MT"},
    "Sapezal": {"lat": -13.1528, "lon": -58.1356, "uf": "MT"},
    "Campo Novo do Parecis": {"lat": -13.7286, "lon": -58.7717, "uf": "MT"},
}

# Mato Grosso do Sul (MS)
CIDADES_MS = {
    "Campo Grande": {"lat": -20.4697, "lon": -54.6201, "uf": "MS"},
    "Dourados": {"lat": -22.2211, "lon": -54.8056, "uf": "MS"},
    "Três Lagoas": {"lat": -20.7511, "lon": -51.6783, "uf": "MS"},
    "Corumbá": {"lat": -19.0078, "lon": -57.6531, "uf": "MS"},
    "Ponta Porã": {"lat": -22.5361, "lon": -55.7256, "uf": "MS"},
    "Aquidauana": {"lat": -20.4708, "lon": -55.7869, "uf": "MS"},
    "Naviraí": {"lat": -23.0656, "lon": -54.1906, "uf": "MS"},
    "Nova Andradina": {"lat": -22.2361, "lon": -53.3436, "uf": "MS"},
    "Sidrolândia": {"lat": -20.9314, "lon": -54.9608, "uf": "MS"},
    "Maracaju": {"lat": -21.6145, "lon": -55.1683, "uf": "MS"},
    "São Gabriel do Oeste": {"lat": -19.3937, "lon": -54.5649, "uf": "MS"},
}

# Minas Gerais (MG)
CIDADES_MG = {
    "Belo Horizonte": {"lat": -19.9167, "lon": -43.9345, "uf": "MG"},
    "Uberlândia": {"lat": -18.9189, "lon": -48.2772, "uf": "MG"},
    "Contagem": {"lat": -19.9320, "lon": -44.0539, "uf": "MG"},
    "Juiz de Fora": {"lat": -21.7642, "lon": -43.3503, "uf": "MG"},
    "Betim": {"lat": -19.9681, "lon": -44.1983, "uf": "MG"},
    "Montes Claros": {"lat": -16.7350, "lon": -43.8619, "uf": "MG"},
    "Ribeirão das Neves": {"lat": -19.7669, "lon": -44.0869, "uf": "MG"},
    "Uberaba": {"lat": -19.7472, "lon": -47.9319, "uf": "MG"},
    "Governador Valadares": {"lat": -18.8511, "lon": -41.9495, "uf": "MG"},
    "Ipatinga": {"lat": -19.4683, "lon": -42.5369, "uf": "MG"},
    "Sete Lagoas": {"lat": -19.4658, "lon": -44.2467, "uf": "MG"},
    "Divinópolis": {"lat": -20.1389, "lon": -44.8839, "uf": "MG"},
    "Santa Luzia": {"lat": -19.7697, "lon": -43.8514, "uf": "MG"},
    "Ibirité": {"lat": -20.0217, "lon": -44.0589, "uf": "MG"},
    "Poços de Caldas": {"lat": -21.7878, "lon": -46.5614, "uf": "MG"},
    "Patos de Minas": {"lat": -18.5789, "lon": -46.5180, "uf": "MG"},
    "Pouso Alegre": {"lat": -22.2300, "lon": -45.9364, "uf": "MG"},
    "Teófilo Otoni": {"lat": -17.8575, "lon": -41.5050, "uf": "MG"},
    "Barbacena": {"lat": -21.2256, "lon": -43.7736, "uf": "MG"},
    "Sabará": {"lat": -19.8850, "lon": -43.8069, "uf": "MG"},
    "Varginha": {"lat": -21.5511, "lon": -45.4331, "uf": "MG"},
    "Conselheiro Lafaiete": {"lat": -20.6600, "lon": -43.7861, "uf": "MG"},
    "Itabira": {"lat": -19.6189, "lon": -43.2269, "uf": "MG"},
    "Araguari": {"lat": -18.6472, "lon": -48.1867, "uf": "MG"},
    "Passos": {"lat": -20.7189, "lon": -46.6100, "uf": "MG"},
    "Paracatu": {"lat": -17.2222, "lon": -46.8747, "uf": "MG"},
}

# Pará (PA)
CIDADES_PA = {
    "Belém": {"lat": -1.4558, "lon": -48.5039, "uf": "PA"},
    "Ananindeua": {"lat": -1.3656, "lon": -48.3722, "uf": "PA"},
    "Santarém": {"lat": -2.4411, "lon": -54.7083, "uf": "PA"},
    "Marabá": {"lat": -5.3686, "lon": -49.1178, "uf": "PA"},
    "Castanhal": {"lat": -1.2933, "lon": -47.9261, "uf": "PA"},
    "Parauapebas": {"lat": -6.0672, "lon": -49.9022, "uf": "PA"},
    "Itaituba": {"lat": -4.2761, "lon": -55.9836, "uf": "PA"},
    "Cametá": {"lat": -2.2428, "lon": -49.4956, "uf": "PA"},
    "Bragança": {"lat": -1.0539, "lon": -46.7656, "uf": "PA"},
    "Abaetetuba": {"lat": -1.7219, "lon": -48.8786, "uf": "PA"},
    "Marituba": {"lat": -1.3631, "lon": -48.3397, "uf": "PA"},
    "Altamira": {"lat": -3.2028, "lon": -52.2097, "uf": "PA"},
    "Paragominas": {"lat": -2.9953, "lon": -47.3522, "uf": "PA"},
}

# Paraíba (PB)
CIDADES_PB = {
    "João Pessoa": {"lat": -7.1195, "lon": -34.8450, "uf": "PB"},
    "Campina Grande": {"lat": -7.2306, "lon": -35.8811, "uf": "PB"},
    "Santa Rita": {"lat": -7.1139, "lon": -34.9778, "uf": "PB"},
    "Patos": {"lat": -7.0244, "lon": -37.2800, "uf": "PB"},
    "Bayeux": {"lat": -7.1303, "lon": -34.9322, "uf": "PB"},
    "Sousa": {"lat": -6.7611, "lon": -38.2278, "uf": "PB"},
    "Cabedelo": {"lat": -6.9811, "lon": -34.8350, "uf": "PB"},
    "Cajazeiras": {"lat": -6.8897, "lon": -38.5558, "uf": "PB"},
}

# Paraná (PR)
CIDADES_PR = {
    "Curitiba": {"lat": -25.4290, "lon": -49.2671, "uf": "PR"},
    "Londrina": {"lat": -23.3045, "lon": -51.1696, "uf": "PR"},
    "Maringá": {"lat": -23.4205, "lon": -51.9331, "uf": "PR"},
    "Ponta Grossa": {"lat": -25.0916, "lon": -50.1668, "uf": "PR"},
    "Cascavel": {"lat": -24.9555, "lon": -53.4552, "uf": "PR"},
    "São José dos Pinhais": {"lat": -25.5347, "lon": -49.2064, "uf": "PR"},
    "Foz do Iguaçu": {"lat": -25.5478, "lon": -54.5882, "uf": "PR"},
    "Colombo": {"lat": -25.2919, "lon": -49.2239, "uf": "PR"},
    "Guarapuava": {"lat": -25.3905, "lon": -51.4621, "uf": "PR"},
    "Paranaguá": {"lat": -25.5200, "lon": -48.5092, "uf": "PR"},
    "Araucária": {"lat": -25.5928, "lon": -49.4097, "uf": "PR"},
    "Toledo": {"lat": -24.7136, "lon": -53.7429, "uf": "PR"},
    "Apucarana": {"lat": -23.5511, "lon": -51.4608, "uf": "PR"},
    "Pinhais": {"lat": -25.4447, "lon": -49.1919, "uf": "PR"},
    "Campo Largo": {"lat": -25.4597, "lon": -49.5272, "uf": "PR"},
    "Almirante Tamandaré": {"lat": -25.3247, "lon": -49.3100, "uf": "PR"},
    "Umuarama": {"lat": -23.7661, "lon": -53.3250, "uf": "PR"},
    "Piraquara": {"lat": -25.4422, "lon": -49.0628, "uf": "PR"},
    "Cambé": {"lat": -23.2761, "lon": -51.2778, "uf": "PR"},
    "Sarandi": {"lat": -23.4444, "lon": -51.8761, "uf": "PR"},
}

# Pernambuco (PE)
CIDADES_PE = {
    "Recife": {"lat": -8.0476, "lon": -34.8770, "uf": "PE"},
    "Jaboatão dos Guararapes": {"lat": -8.1130, "lon": -35.0150, "uf": "PE"},
    "Olinda": {"lat": -8.0089, "lon": -34.8553, "uf": "PE"},
    "Paulista": {"lat": -7.9406, "lon": -34.8728, "uf": "PE"},
    "Caruaru": {"lat": -8.2839, "lon": -35.9761, "uf": "PE"},
    "Petrolina": {"lat": -9.3891, "lon": -40.5008, "uf": "PE"},
    "Cabo de Santo Agostinho": {"lat": -8.2814, "lon": -35.0350, "uf": "PE"},
    "Camaragibe": {"lat": -8.0239, "lon": -35.0386, "uf": "PE"},
    "Garanhuns": {"lat": -8.8900, "lon": -36.4928, "uf": "PE"},
    "Vitória de Santo Antão": {"lat": -8.1189, "lon": -35.2917, "uf": "PE"},
}

# Piauí (PI)
CIDADES_PI = {
    "Teresina": {"lat": -5.0892, "lon": -42.8019, "uf": "PI"},
    "Parnaíba": {"lat": -2.9053, "lon": -41.7767, "uf": "PI"},
    "Picos": {"lat": -7.0769, "lon": -41.4669, "uf": "PI"},
    "Floriano": {"lat": -6.7697, "lon": -43.0228, "uf": "PI"},
    "Piripiri": {"lat": -4.2728, "lon": -41.7756, "uf": "PI"},
    "Campo Maior": {"lat": -4.8281, "lon": -42.1678, "uf": "PI"},
    "Uruçuí": {"lat": -7.2336, "lon": -44.5517, "uf": "PI"},
    "Bom Jesus": {"lat": -9.0747, "lon": -44.3589, "uf": "PI"},
    "Baixa Grande do Ribeiro": {"lat": -7.8689, "lon": -45.2361, "uf": "PI"},
}

# Rio de Janeiro (RJ)
CIDADES_RJ = {
    "Rio de Janeiro": {"lat": -22.9068, "lon": -43.1729, "uf": "RJ"},
    "São Gonçalo": {"lat": -22.8268, "lon": -43.0539, "uf": "RJ"},
    "Duque de Caxias": {"lat": -22.7858, "lon": -43.3053, "uf": "RJ"},
    "Nova Iguaçu": {"lat": -22.7592, "lon": -43.4511, "uf": "RJ"},
    "Niterói": {"lat": -22.8833, "lon": -43.1036, "uf": "RJ"},
    "Belford Roxo": {"lat": -22.7642, "lon": -43.3997, "uf": "RJ"},
    "Campos dos Goytacazes": {"lat": -21.7622, "lon": -41.3181, "uf": "RJ"},
    "São João de Meriti": {"lat": -22.8042, "lon": -43.3722, "uf": "RJ"},
    "Petrópolis": {"lat": -22.5050, "lon": -43.1789, "uf": "RJ"},
    "Volta Redonda": {"lat": -22.5231, "lon": -44.1042, "uf": "RJ"},
    "Magé": {"lat": -22.6528, "lon": -43.0403, "uf": "RJ"},
    "Itaboraí": {"lat": -22.7447, "lon": -42.8597, "uf": "RJ"},
    "Macaé": {"lat": -22.3708, "lon": -41.7869, "uf": "RJ"},
    "Cabo Frio": {"lat": -22.8794, "lon": -42.0186, "uf": "RJ"},
    "Nova Friburgo": {"lat": -22.2819, "lon": -42.5311, "uf": "RJ"},
}

# Rio Grande do Norte (RN)
CIDADES_RN = {
    "Natal": {"lat": -5.7945, "lon": -35.2110, "uf": "RN"},
    "Mossoró": {"lat": -5.1878, "lon": -37.3439, "uf": "RN"},
    "Parnamirim": {"lat": -5.9153, "lon": -35.2628, "uf": "RN"},
    "São Gonçalo do Amarante": {"lat": -5.7928, "lon": -35.3267, "uf": "RN"},
    "Macaíba": {"lat": -5.8586, "lon": -35.3597, "uf": "RN"},
    "Ceará-Mirim": {"lat": -5.6339, "lon": -35.4256, "uf": "RN"},
    "Caicó": {"lat": -6.4578, "lon": -37.0978, "uf": "RN"},
    "Açu": {"lat": -5.5786, "lon": -36.9094, "uf": "RN"},
}

# Rio Grande do Sul (RS)
CIDADES_RS = {
    "Porto Alegre": {"lat": -30.0346, "lon": -51.2177, "uf": "RS"},
    "Caxias do Sul": {"lat": -29.1631, "lon": -51.1794, "uf": "RS"},
    "Pelotas": {"lat": -31.7719, "lon": -52.3425, "uf": "RS"},
    "Canoas": {"lat": -29.9178, "lon": -51.1839, "uf": "RS"},
    "Santa Maria": {"lat": -29.6842, "lon": -53.8069, "uf": "RS"},
    "Gravataí": {"lat": -29.9439, "lon": -50.9919, "uf": "RS"},
    "Viamão": {"lat": -30.0811, "lon": -51.0236, "uf": "RS"},
    "Novo Hamburgo": {"lat": -29.6783, "lon": -51.1306, "uf": "RS"},
    "São Leopoldo": {"lat": -29.7600, "lon": -51.1478, "uf": "RS"},
    "Rio Grande": {"lat": -32.0350, "lon": -52.0986, "uf": "RS"},
    "Alvorada": {"lat": -29.9897, "lon": -51.0797, "uf": "RS"},
    "Passo Fundo": {"lat": -28.2623, "lon": -52.4083, "uf": "RS"},
    "Sapucaia do Sul": {"lat": -29.8289, "lon": -51.1461, "uf": "RS"},
    "Uruguaiana": {"lat": -29.7546, "lon": -57.0883, "uf": "RS"},
    "Santa Cruz do Sul": {"lat": -29.7178, "lon": -52.4261, "uf": "RS"},
    "Cachoeirinha": {"lat": -29.9508, "lon": -51.0939, "uf": "RS"},
    "Bagé": {"lat": -31.3314, "lon": -54.1069, "uf": "RS"},
    "Bento Gonçalves": {"lat": -29.1678, "lon": -51.5189, "uf": "RS"},
    "Erechim": {"lat": -27.6339, "lon": -52.2736, "uf": "RS"},
    "Guaíba": {"lat": -30.1139, "lon": -51.3253, "uf": "RS"},
    "Cruz Alta": {"lat": -28.6386, "lon": -53.6061, "uf": "RS"},
    "Ijuí": {"lat": -28.3878, "lon": -53.9147, "uf": "RS"},
}

# Rondônia (RO)
CIDADES_RO = {
    "Porto Velho": {"lat": -8.7619, "lon": -63.9039, "uf": "RO"},
    "Ji-Paraná": {"lat": -10.8786, "lon": -61.9514, "uf": "RO"},
    "Ariquemes": {"lat": -9.9131, "lon": -63.0408, "uf": "RO"},
    "Vilhena": {"lat": -12.7404, "lon": -60.1458, "uf": "RO"},
    "Cacoal": {"lat": -11.4386, "lon": -61.4472, "uf": "RO"},
    "Jaru": {"lat": -10.4394, "lon": -62.4664, "uf": "RO"},
    "Rolim de Moura": {"lat": -11.7272, "lon": -61.7739, "uf": "RO"},
}

# Roraima (RR)
CIDADES_RR = {
    "Boa Vista": {"lat": 2.8235, "lon": -60.6758, "uf": "RR"},
    "Rorainópolis": {"lat": -0.9403, "lon": -60.4403, "uf": "RR"},
    "Caracaraí": {"lat": 1.8167, "lon": -61.1281, "uf": "RR"},
    "Alto Alegre": {"lat": 2.9956, "lon": -61.3103, "uf": "RR"},
}

# Santa Catarina (SC)
CIDADES_SC = {
    "Joinville": {"lat": -26.3044, "lon": -48.8461, "uf": "SC"},
    "Florianópolis": {"lat": -27.5954, "lon": -48.5480, "uf": "SC"},
    "Blumenau": {"lat": -26.9194, "lon": -49.0661, "uf": "SC"},
    "São José": {"lat": -27.6103, "lon": -48.6350, "uf": "SC"},
    "Criciúma": {"lat": -28.6778, "lon": -49.3697, "uf": "SC"},
    "Chapecó": {"lat": -27.0965, "lon": -52.6158, "uf": "SC"},
    "Itajaí": {"lat": -26.9078, "lon": -48.6619, "uf": "SC"},
    "Jaraguá do Sul": {"lat": -26.4861, "lon": -49.0772, "uf": "SC"},
    "Lages": {"lat": -27.8147, "lon": -50.3261, "uf": "SC"},
    "Palhoça": {"lat": -27.6447, "lon": -48.6703, "uf": "SC"},
    "Balneário Camboriú": {"lat": -26.9906, "lon": -48.6350, "uf": "SC"},
    "Brusque": {"lat": -27.0981, "lon": -48.9139, "uf": "SC"},
    "Tubarão": {"lat": -28.4669, "lon": -49.0069, "uf": "SC"},
    "São Bento do Sul": {"lat": -26.2489, "lon": -49.3797, "uf": "SC"},
    "Caçador": {"lat": -26.7753, "lon": -51.0150, "uf": "SC"},
    "Campos Novos": {"lat": -27.4004, "lon": -51.2254, "uf": "SC"},
}

# São Paulo (SP)
CIDADES_SP = {
    "São Paulo": {"lat": -23.5505, "lon": -46.6333, "uf": "SP"},
    "Guarulhos": {"lat": -23.4538, "lon": -46.5333, "uf": "SP"},
    "Campinas": {"lat": -22.9099, "lon": -47.0626, "uf": "SP"},
    "São Bernardo do Campo": {"lat": -23.6914, "lon": -46.5647, "uf": "SP"},
    "Santo André": {"lat": -23.6636, "lon": -46.5336, "uf": "SP"},
    "Osasco": {"lat": -23.5329, "lon": -46.7919, "uf": "SP"},
    "São José dos Campos": {"lat": -23.2237, "lon": -45.9009, "uf": "SP"},
    "Ribeirão Preto": {"lat": -21.1704, "lon": -47.8103, "uf": "SP"},
    "Sorocaba": {"lat": -23.5015, "lon": -47.4526, "uf": "SP"},
    "Mauá": {"lat": -23.6678, "lon": -46.4611, "uf": "SP"},
    "São José do Rio Preto": {"lat": -20.8197, "lon": -49.3794, "uf": "SP"},
    "Santos": {"lat": -23.9608, "lon": -46.3336, "uf": "SP"},
    "Mogi das Cruzes": {"lat": -23.5228, "lon": -46.1883, "uf": "SP"},
    "Diadema": {"lat": -23.6861, "lon": -46.6228, "uf": "SP"},
    "Jundiaí": {"lat": -23.1864, "lon": -46.8842, "uf": "SP"},
    "Carapicuíba": {"lat": -23.5225, "lon": -46.8356, "uf": "SP"},
    "Piracicaba": {"lat": -22.7253, "lon": -47.6492, "uf": "SP"},
    "Bauru": {"lat": -22.3147, "lon": -49.0608, "uf": "SP"},
    "Itaquaquecetuba": {"lat": -23.4864, "lon": -46.3486, "uf": "SP"},
    "São Vicente": {"lat": -23.9633, "lon": -46.3919, "uf": "SP"},
    "Franca": {"lat": -20.5386, "lon": -47.4008, "uf": "SP"},
    "Guarujá": {"lat": -23.9931, "lon": -46.2564, "uf": "SP"},
    "Taubaté": {"lat": -23.0264, "lon": -45.5553, "uf": "SP"},
    "Limeira": {"lat": -22.5647, "lon": -47.4017, "uf": "SP"},
    "Suzano": {"lat": -23.5428, "lon": -46.3108, "uf": "SP"},
    "Taboão da Serra": {"lat": -23.6028, "lon": -46.7578, "uf": "SP"},
    "Sumaré": {"lat": -22.8219, "lon": -47.2669, "uf": "SP"},
    "Barueri": {"lat": -23.5106, "lon": -46.8764, "uf": "SP"},
    "Embu das Artes": {"lat": -23.6489, "lon": -46.8522, "uf": "SP"},
    "São Carlos": {"lat": -22.0175, "lon": -47.8908, "uf": "SP"},
    "Marília": {"lat": -22.2139, "lon": -49.9456, "uf": "SP"},
    "Indaiatuba": {"lat": -23.0903, "lon": -47.2181, "uf": "SP"},
    "Cotia": {"lat": -23.6039, "lon": -46.9192, "uf": "SP"},
    "Americana": {"lat": -22.7389, "lon": -47.3314, "uf": "SP"},
    "Araraquara": {"lat": -21.7947, "lon": -48.1758, "uf": "SP"},
    "Jacareí": {"lat": -23.3053, "lon": -45.9656, "uf": "SP"},
    "Presidente Prudente": {"lat": -22.1256, "lon": -51.3888, "uf": "SP"},
    "Hortolândia": {"lat": -22.8583, "lon": -47.2200, "uf": "SP"},
    "Araçatuba": {"lat": -21.2089, "lon": -50.4328, "uf": "SP"},
    "Santa Bárbara d'Oeste": {"lat": -22.7536, "lon": -47.4142, "uf": "SP"},
    "Jaboticabal": {"lat": -21.2524, "lon": -48.3227, "uf": "SP"},
}

# Sergipe (SE)
CIDADES_SE = {
    "Aracaju": {"lat": -10.9472, "lon": -37.0731, "uf": "SE"},
    "Nossa Senhora do Socorro": {"lat": -10.8550, "lon": -37.1261, "uf": "SE"},
    "Lagarto": {"lat": -10.9167, "lon": -37.6444, "uf": "SE"},
    "Itabaiana": {"lat": -10.6850, "lon": -37.4256, "uf": "SE"},
    "São Cristóvão": {"lat": -11.0142, "lon": -37.2064, "uf": "SE"},
    "Estância": {"lat": -11.2681, "lon": -37.4456, "uf": "SE"},
}

# Tocantins (TO)
CIDADES_TO = {
    "Palmas": {"lat": -10.1842, "lon": -48.3336, "uf": "TO"},
    "Araguaína": {"lat": -7.1911, "lon": -48.2072, "uf": "TO"},
    "Gurupi": {"lat": -11.7292, "lon": -49.0683, "uf": "TO"},
    "Porto Nacional": {"lat": -10.7081, "lon": -48.4172, "uf": "TO"},
    "Paraíso do Tocantins": {"lat": -10.1758, "lon": -48.8822, "uf": "TO"},
    "Araguatins": {"lat": -5.6486, "lon": -48.1242, "uf": "TO"},
    "Tocantinópolis": {"lat": -6.3258, "lon": -47.4117, "uf": "TO"},
}

# Consolida todas as cidades de todos os estados
TODAS_CIDADES = {
    **CIDADES_AC,
    **CIDADES_AL,
    **CIDADES_AP,
    **CIDADES_AM,
    **CIDADES_BA,
    **CIDADES_CE,
    **CIDADES_DF,
    **CIDADES_ES,
    **CIDADES_GO,
    **CIDADES_MA,
    **CIDADES_MT,
    **CIDADES_MS,
    **CIDADES_MG,
    **CIDADES_PA,
    **CIDADES_PB,
    **CIDADES_PR,
    **CIDADES_PE,
    **CIDADES_PI,
    **CIDADES_RJ,
    **CIDADES_RN,
    **CIDADES_RS,
    **CIDADES_RO,
    **CIDADES_RR,
    **CIDADES_SC,
    **CIDADES_SP,
    **CIDADES_SE,
    **CIDADES_TO,
}


class ClimateService:
    """Serviço de análise climática."""
    
    def __init__(self):
        """Inicializa o serviço climático."""
        self.cache = {}
    
    def get_cidades_disponiveis(self, estado: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Retorna lista de cidades disponíveis.
        
        Args:
            estado: Filtrar por UF (opcional)
        
        Returns:
            Dicionário com cidades e coordenadas
        """
        if estado:
            return {k: v for k, v in TODAS_CIDADES.items() if v.get('uf') == estado}
        return TODAS_CIDADES
    
    def get_coordenadas_cidade(self, cidade: str) -> Optional[Dict[str, float]]:
        """
        Retorna coordenadas de uma cidade.
        
        Args:
            cidade: Nome da cidade
        
        Returns:
            Dicionário com lat/lon ou None
        """
        return TODAS_CIDADES.get(cidade)
    
    def buscar_dados_clima(
        self,
        lat: float,
        lon: float,
        years: int = 2,
        media_historica: float = 600.0,
        cache_days: int = 30,
        redis_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Busca dados climáticos para uma localização.
        
        Args:
            lat: Latitude
            lon: Longitude
            years: Anos retroativos
            media_historica: Média histórica de precipitação (mm)
            cache_days: Dias de validade do cache
            redis_url: URL do Redis (opcional)
        
        Returns:
            Resultado com data, precipitacoes, fator e summary
        """
        cache_key = f"{lat}_{lon}_{years}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        config = {
            'lat': lat,
            'lon': lon,
            'years': years,
            'media_historica': media_historica,
            'cache_days': cache_days,
            'redis_url': redis_url,
        }
        
        try:
            resultado = fetch_climate(config)
            self.cache[cache_key] = resultado
            return resultado
        except Exception as e:
            return {
                'error': str(e),
                'data': None,
                'precipitacoes': None,
                'fator': None,
                'summary': None
            }
    
    def buscar_por_cidade(
        self,
        cidade: str,
        years: int = 2,
        media_historica: float = 600.0
    ) -> Dict[str, Any]:
        """
        Busca dados climáticos por nome de cidade.
        
        Args:
            cidade: Nome da cidade
            years: Anos retroativos
            media_historica: Média histórica de precipitação (mm)
        
        Returns:
            Resultado climático
        """
        coords = self.get_coordenadas_cidade(cidade)
        if not coords:
            return {'error': f'Cidade não encontrada: {cidade}'}
        
        return self.buscar_dados_clima(
            lat=coords['lat'],
            lon=coords['lon'],
            years=years,
            media_historica=media_historica
        )
    
    def comparar_localizacoes(
        self,
        localizacoes: List[Dict[str, Any]],
        years: int = 2
    ) -> pd.DataFrame:
        """
        Compara dados climáticos de múltiplas localizações.
        
        Args:
            localizacoes: Lista de dicts com 'nome', 'lat', 'lon', 'media_historica'
            years: Anos retroativos
        
        Returns:
            DataFrame comparativo
        """
        resultados = []
        
        for loc in localizacoes:
            dados = self.buscar_dados_clima(
                lat=loc['lat'],
                lon=loc['lon'],
                years=years,
                media_historica=loc.get('media_historica', 600.0)
            )
            
            summary = dados.get('summary', {})
            resultados.append({
                'nome': loc.get('nome', f"Lat {loc['lat']}, Lon {loc['lon']}"),
                'fator_clima': dados.get('fator'),
                'precip_media_safra': summary.get('precip_media_safra'),
                'precip_mais_recente': summary.get('precipitacao_mais_recente'),
                'precip_relativa': summary.get('precipitacao_relativa'),
                'anos_usados': summary.get('used_years'),
                'metodo': summary.get('fetch_method'),
            })
        
        return pd.DataFrame(resultados)
    
    def interpretar_fator_clima(self, fator: Optional[float]) -> str:
        """
        Interpreta o fator climático em texto.
        
        Args:
            fator: Fator de impacto climático
        
        Returns:
            Interpretação textual
        """
        if fator is None:
            return "Dados insuficientes"
        
        if fator >= 1.2:
            return "🟢 Excelente - Precipitação muito acima da média (+20%)"
        elif fator >= 1.05:
            return "🟢 Bom - Precipitação acima da média (+5% a +20%)"
        elif fator >= 0.95:
            return "🟡 Normal - Precipitação dentro da média (±5%)"
        elif fator >= 0.80:
            return "🟠 Abaixo - Precipitação abaixo da média (-5% a -20%)"
        else:
            return "🔴 Crítico - Precipitação muito abaixo da média (>-20%)"
    
    def calcular_ajuste_produtividade(self, fator: Optional[float]) -> float:
        """
        Calcula ajuste percentual na produtividade baseado no clima.
        
        Args:
            fator: Fator climático
        
        Returns:
            Percentual de ajuste (-1.0 a 1.0)
        """
        if fator is None:
            return 0.0
        
        # Fator 1.0 = sem ajuste, >1.0 = aumento, <1.0 = redução
        return (fator - 1.0)
