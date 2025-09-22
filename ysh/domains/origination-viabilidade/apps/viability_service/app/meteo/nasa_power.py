"""Funções para obtenção de dados meteorológicos da NASA POWER.

Adaptado de pvlib para uso no serviço de viabilidade.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests

URL = 'https://power.larc.nasa.gov/api/temporal/hourly/point'

DEFAULT_PARAMETERS = [
    'dni', 'dhi', 'ghi', 'temp_air', 'wind_speed'
]

VARIABLE_MAP = {
    'ALLSKY_SFC_SW_DWN': 'ghi',
    'ALLSKY_SFC_SW_DIFF': 'dhi',
    'ALLSKY_SFC_SW_DNI': 'dni',
    'CLRSKY_SFC_SW_DWN': 'ghi_clear',
    'T2M': 'temp_air',
    'WS2M': 'wind_speed_2m',
    'WS10M': 'wind_speed',
}


def get_nasa_power(latitude: float, longitude: float,
                   start: Optional[datetime] = None,
                   end: Optional[datetime] = None,
                   parameters: List[str] = DEFAULT_PARAMETERS,
                   *, community: str = 're',
                   elevation: Optional[float] = None,
                   wind_height: Optional[float] = None,
                   wind_surface: Optional[str] = None,
                   map_variables: bool = True,
                   url: str = URL) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Obtém dados de irradiância e meteorologia da NASA POWER.

    Parâmetros
    ----------
    latitude: float
        Em graus decimais, norte é positivo (ISO 19115).
    longitude: float
        Em graus decimais, leste é positivo (ISO 19115).
    start: datetime, opcional
        Primeira data do período solicitado. Se None, usa o início do ano atual.
    end: datetime, opcional
        Última data do período solicitado. Se None, usa a data atual.
    parameters: str, list
        Lista de parâmetros. Os parâmetros padrão são mencionados abaixo.

        * Global Horizontal Irradiance (GHI) [Wm⁻²]
        * Diffuse Horizontal Irradiance (DHI) [Wm⁻²]
        * Direct Normal Irradiance (DNI) [Wm⁻²]
        * Air temperature at 2 m [C]
        * Wind speed at 10 m [m/s]

    community: str, default 're'
        Pode ser um dos seguintes dependendo de quais parâmetros são de interesse:
        * ``'re'``: energia renovável
        * ``'sb'``: construções sustentáveis
        * ``'ag'``: agroclimatologia

    elevation: float, opcional
        Elevação do local em metros para produzir a pressão atmosférica corrigida.
    wind_height: float, opcional
        Altura do vento em metros para produzir a velocidade do vento ajustada para altura.
    wind_surface: str, opcional
        Tipo de superfície para ajustar a velocidade do vento.
    map_variables: bool, default True
        Quando True, renomeia as colunas do DataFrame para nomes de variáveis pvlib.

    Retorna
    -------
    data : pd.DataFrame
        Dados de série temporal. O índice corresponde ao início (esquerda) do intervalo.
    meta : dict
        Metadados.
    """
    # Se start/end não forem fornecidos, use valores padrão
    if start is None:
        start = datetime(datetime.now().year, 1, 1)
    if end is None:
        end = datetime.now()

    # Garantir que não estamos solicitando mais de 365 dias (limite da API NASA POWER)
    days_diff = (end - start).days
    if days_diff > 365:
        end = start + timedelta(days=365)

    start = pd.Timestamp(start)
    end = pd.Timestamp(end)

    # permite o uso de nomes de parâmetros pvlib
    parameter_dict = {v: k for k, v in VARIABLE_MAP.items()}
    parameters = [parameter_dict.get(p, p) for p in parameters]

    params = {
        'latitude': latitude,
        'longitude': longitude,
        'start': start.strftime('%Y%m%d'),
        'end': end.strftime('%Y%m%d'),
        'community': community,
        'parameters': ','.join(parameters),  # torna parâmetros em uma string
        'format': 'json',
        'user': None,
        'header': True,
        'time-standard': 'utc',
        'site-elevation': elevation,
        'wind-elevation': wind_height,
        'wind-surface': wind_surface,
    }

    try:
        response = requests.get(url, params=params)
        if not response.ok:
            # response.raise_for_status() não fornece uma mensagem de erro útil
            error_msg = response.json() if response.content else f"Erro HTTP {response.status_code}"
            raise requests.HTTPError(f"Falha ao acessar NASA POWER: {error_msg}")

        # Analisa os dados para dataframe
        data = response.json()
        hourly_data = data['properties']['parameter']
        df = pd.DataFrame(hourly_data)
        df.index = pd.to_datetime(df.index, format='%Y%m%d%H').tz_localize('UTC')

        # Cria dicionário de metadados
        meta = data['header']
        meta['times'] = data['times']
        meta['parameters'] = data['parameters']

        meta['longitude'] = data['geometry']['coordinates'][0]
        meta['latitude'] = data['geometry']['coordinates'][1]
        meta['altitude'] = data['geometry']['coordinates'][2]

        # Substitui valores NaN
        df = df.replace(meta['fill_value'], np.nan)

        # Renomeia de acordo com a convenção pvlib
        if map_variables:
            df = df.rename(columns=VARIABLE_MAP)

        return df, meta
    except Exception as e:
        # Tratamento de erro mais robusto
        error_msg = f"Erro ao obter dados NASA POWER: {str(e)}"
        print(error_msg)
        # Retorna DataFrame vazio e metadados mínimos em caso de erro
        empty_df = pd.DataFrame(columns=VARIABLE_MAP.values())
        empty_meta = {
            'latitude': latitude,
            'longitude': longitude,
            'error': error_msg
        }
        return empty_df, empty_meta


def get_annual_insolation(latitude: float, longitude: float) -> Dict[str, float]:
    """
    Calcula a insolação anual para um determinado local usando dados NASA POWER.

    Parâmetros
    ----------
    latitude: float
        Em graus decimais, norte é positivo
    longitude: float
        Em graus decimais, leste é positivo

    Retorna
    -------
    dict
        Dicionário com valores de insolação anual (kWh/m²/ano) e DNI anual (kWh/m²/ano)
    """
    try:
        # Obtém dados para o último ano completo
        end = datetime.now()
        start = datetime(end.year - 1, end.month, end.day)

        df, meta = get_nasa_power(latitude, longitude, start, end)

        # Verifica se temos dados suficientes
        if df.empty or len(df) < 24:  # Pelo menos um dia
            return {
                'ghi_annual': 1825.0,  # 5 kWh/m²/dia * 365 dias (valor médio para Brasil)
                'dni_annual': 2007.5,  # 5.5 kWh/m²/dia * 365 dias (valor médio para Brasil)
                'is_estimated': True
            }

        # Converte de W/m² para kWh/m²/hora (dividindo por 1000)
        if 'ghi' in df.columns:
            df['ghi_kwh'] = df['ghi'] / 1000
        else:
            df['ghi_kwh'] = 0

        if 'dni' in df.columns:
            df['dni_kwh'] = df['dni'] / 1000
        else:
            df['dni_kwh'] = 0

        # Soma todos os valores horários para obter kWh/m²/ano
        ghi_annual = df['ghi_kwh'].sum()
        dni_annual = df['dni_kwh'].sum()

        # Ajusta para um ano completo se necessário
        hours_in_data = len(df)
        if hours_in_data < 8760:  # menos que um ano
            scaling_factor = 8760 / hours_in_data
            ghi_annual *= scaling_factor
            dni_annual *= scaling_factor

        return {
            'ghi_annual': round(ghi_annual, 1),
            'dni_annual': round(dni_annual, 1),
            'is_estimated': False
        }
    except Exception as e:
        print(f"Erro ao calcular insolação anual: {str(e)}")
        # Valores médios para o Brasil em caso de falha
        return {
            'ghi_annual': 1825.0,  # 5 kWh/m²/dia * 365 dias
            'dni_annual': 2007.5,  # 5.5 kWh/m²/dia * 365 dias
            'is_estimated': True
        }            'is_estimated': True
        }
