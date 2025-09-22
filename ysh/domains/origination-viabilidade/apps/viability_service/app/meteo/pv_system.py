"""Funções para cálculo de sistemas fotovoltaicos usando pvlib."""

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

try:
    import pvlib
    from pvlib import location, modelchain, pvsystem
    from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
except ImportError:
    print("Aviso: pvlib não encontrado. Usando estimativas simplificadas.")

from app.meteo.nasa_power import get_annual_insolation, get_nasa_power


def estimate_pv_performance(
    latitude: float,
    longitude: float,
    tilt: float = 20,
    azimuth: float = 180,  # Sul = 180, Norte = 0
    mount_type: str = "fixed",
    system_loss: float = 0.14,
    meteo_source: str = "NASA_POWER",
) -> Dict[str, Any]:
    """
    Estima a performance de um sistema fotovoltaico de 1kWp.

    Parâmetros
    ----------
    latitude: float
        Latitude em graus decimais
    longitude: float
        Longitude em graus decimais
    tilt: float, default 20
        Inclinação dos módulos em graus
    azimuth: float, default 180
        Azimute dos módulos em graus (Sul = 180, Norte = 0)
    mount_type: str, default "fixed"
        Tipo de montagem: "fixed" ou "single_axis_tracker"
    system_loss: float, default 0.14
        Fração de perdas do sistema (soiling, cabos, inversores, etc.)
    meteo_source: str, default "NASA_POWER"
        Fonte de dados meteorológicos: "NASA_POWER" ou "CLEARSKY_ONLY"

    Retorna
    -------
    Dict
        Dicionário com métricas de performance, incluindo kWh/ano e PR
    """
    # Para o hemisfério sul, ajusta o azimuth padrão
    if latitude < 0 and azimuth == 180:
        azimuth = 0  # Norte para hemisfério sul

    try:
        # Verifica se pvlib está disponível
        if 'pvlib' not in globals():
            # Se pvlib não estiver disponível, usa estimativa simplificada
            return simplified_estimate(latitude, longitude, system_loss)

        # Se meteo_source for CLEARSKY_ONLY, não tentamos buscar dados NASA
        if meteo_source == "CLEARSKY_ONLY":
            return clearsky_estimate(latitude, longitude, tilt, azimuth, system_loss)

        # Obtém dados meteorológicos da NASA POWER
        # Limitamos a 30 dias para estimativa rápida
        end = datetime.now()
        start = datetime(end.year, 1, 1)  # Começa no início do ano atual

        weather, meta = get_nasa_power(latitude, longitude, start, end)

        if weather.empty:
            # Se falhou em obter dados NASA, usa clearsky
            return clearsky_estimate(latitude, longitude, tilt, azimuth, system_loss)

        # Cria objeto Location do pvlib
        loc = location.Location(latitude, longitude, tz='UTC', altitude=meta.get('altitude', 0))

        # Define o sistema fotovoltaico (1 kWp padrão)
        module_parameters = {
            'pdc0': 1000,  # Potência nominal de 1kWp
            'gamma_pdc': -0.004  # Coeficiente de temperatura típico
        }

        inverter_parameters = {
            'pdc0': 1100,  # Potência DC nominal (oversizing de 10%)
            'eta_inv_nom': 0.96  # Eficiência nominal
        }

        # Configura o sistema
        system = pvsystem.PVSystem(
            surface_tilt=tilt,
            surface_azimuth=azimuth,
            module_parameters=module_parameters,
            inverter_parameters=inverter_parameters,
            losses_parameters={'dc_ohmic_percent': system_loss * 100}
        )

        # Configura o modelchain
        mc = modelchain.ModelChain(
            system, loc,
            aoi_model='physical',
            spectral_model='no_loss',
            temperature_model='sapm',
            losses_model='pvwatts'
        )

        # Executa o modelchain
        mc.run_model(weather)

        # Obtém a energia AC anual
        ac_annual = mc.results.ac.sum() / 1000  # Converte de W para kWh

        # Estima PR (Performance Ratio)
        # PR = AC Energy / (Plane of Array Irradiance * System Size * (1 - system_loss))
        poa_annual = mc.results.total_irrad['poa_global'].sum()
        pr = ac_annual / (poa_annual * system.module_parameters['pdc0'] / 1e6)

        # Ajusta para um ano completo
        hours_in_data = len(weather)
        if hours_in_data < 8760:  # menos que um ano
            scaling_factor = 8760 / hours_in_data
            ac_annual *= scaling_factor

        return {
            'kwh_year': round(ac_annual, 1),
            'pr': round(pr, 3),
            'mc_result': {
                'poa_annual': round(poa_annual * scaling_factor, 1),
                'system_size_kw': 1.0,
                'data_source': f"NASA POWER ({hours_in_data} horas)",
                'mount_type': mount_type,
                'tilt': tilt,
                'azimuth': azimuth
            }
        }
    except Exception as e:
        print(f"Erro ao estimar performance PV com pvlib: {str(e)}")
        # Em caso de erro, usa estimativa simplificada
        return simplified_estimate(latitude, longitude, system_loss)


def clearsky_estimate(
    latitude: float,
    longitude: float,
    tilt: float = 20,
    azimuth: float = 180,
    system_loss: float = 0.14
) -> Dict[str, Any]:
    """
    Estima a performance usando apenas o modelo de céu limpo.

    Usa o modelo de céu limpo do pvlib para estimar a geração sem
    dados meteorológicos reais.
    """
    try:
        # Cria objeto Location do pvlib
        loc = location.Location(latitude, longitude, tz='UTC')

        # Calcula posições solares para um ano típico (de 12 em 12 horas para rapidez)
        times = pd.date_range(
            start=f"{datetime.now().year}-01-01",
            end=f"{datetime.now().year}-12-31 23:00:00",
            freq='12H', tz='UTC'
        )

        # Calcula posições solares
        solar_position = loc.get_solarposition(times)

        # Calcula clearsky
        clearsky = loc.get_clearsky(times)

        # Calcula irradiância no plano do array
        poa_irradiance = pvlib.irradiance.get_total_irradiance(
            surface_tilt=tilt,
            surface_azimuth=azimuth,
            solar_zenith=solar_position['zenith'],
            solar_azimuth=solar_position['azimuth'],
            dni=clearsky['dni'],
            ghi=clearsky['ghi'],
            dhi=clearsky['dhi'],
            dni_extra=None,
            model='haydavies'
        )

        # Estima geração (simplificada)
        # Soma POA global e aplica eficiência típica
        poa_annual = poa_irradiance['poa_global'].sum()

        # Eficiência típica de 15% para o módulo e 96% para o inversor
        system_efficiency = 0.15 * 0.96 * (1 - system_loss)

        # Calcula kWh anual para 1kWp
        kwh_annual = poa_annual * system_efficiency / 1000  # Converte de W para kWh

        # Ajusta para um ano completo (os timestamps são de 12 em 12 horas)
        scaling_factor = 8760 / len(times)
        kwh_annual *= scaling_factor

        # PR típico para sistema bem dimensionado
        pr = 0.80 * (1 - system_loss)

        return {
            'kwh_year': round(kwh_annual, 1),
            'pr': round(pr, 3),
            'mc_result': {
                'poa_annual': round(poa_annual * scaling_factor, 1),
                'system_size_kw': 1.0,
                'data_source': "Clearsky Model",
                'mount_type': "fixed",
                'tilt': tilt,
                'azimuth': azimuth
            }
        }
    except Exception as e:
        print(f"Erro ao estimar com clearsky: {str(e)}")
        return simplified_estimate(latitude, longitude, system_loss)


def simplified_estimate(
    latitude: float,
    longitude: float,
    system_loss: float = 0.14
) -> Dict[str, Any]:
    """
    Estimativa simplificada baseada em médias regionais.

    Usado como fallback quando pvlib ou dados meteorológicos não
    estão disponíveis.
    """
    # Tenta obter insolação anual do NASA POWER
    insolation = get_annual_insolation(latitude, longitude)

    # HSP = Horas de Sol Pleno (kWh/m²/dia)
    if not insolation['is_estimated']:
        # Se temos dados reais, usa eles
        ghi_annual = insolation['ghi_annual']
        hsp = ghi_annual / 365.0
    else:
        # Estimativa por região do Brasil (baseado em Atlas Solarimétrico)
        if -30 <= latitude <= -10 and -60 <= longitude <= -40:  # Sul/Sudeste
            hsp = 4.8
        elif -10 <= latitude <= 0 and -70 <= longitude <= -35:  # Centro-Oeste/Nordeste
            hsp = 5.5
        elif 0 <= latitude <= 5 and -70 <= longitude <= -45:  # Norte
            hsp = 5.2
        else:
            hsp = 5.0  # Valor médio para o Brasil

    # PR típico para sistema bem dimensionado
    pr = 0.80 * (1 - system_loss)

    # kWh/kWp/ano = HSP * 365 * PR
    kwh_per_kwp_year = hsp * 365 * pr

    return {
        'kwh_year': round(kwh_per_kwp_year, 1),
        'pr': round(pr, 3),
        'mc_result': {
            'hsp': round(hsp, 2),
            'system_size_kw': 1.0,
            'data_source': "Simplified Estimate" if insolation['is_estimated'] else "NASA POWER Annual",
            'mount_type': "fixed",
            'tilt': "optimal",
            'azimuth': "optimal"
        }
    }            'azimuth': "optimal"
        }
    }
