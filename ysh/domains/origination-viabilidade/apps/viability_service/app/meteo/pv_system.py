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


def _safe_float(value: Any) -> Optional[float]:
    """Converte valores numéricos em float, protegendo contra NaN."""

    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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

        # Executa o modelchain com a série NASA POWER
        mc.run_model(weather)

        solar_position = loc.get_solarposition(weather.index)
        min_zenith = _safe_float(solar_position['zenith'].min()) or 0.0
        max_elevation = _safe_float(solar_position['elevation'].max()) or 0.0
        solar_hours = len(weather)

        ac_annual = mc.results.ac.sum() / 1000  # W → kWh
        poa_annual = mc.results.total_irrad['poa_global'].sum()

        scaling_factor = 1.0
        if solar_hours and solar_hours < 8760:
            scaling_factor = 8760 / solar_hours
            ac_annual *= scaling_factor
            poa_annual *= scaling_factor

        if poa_annual > 0:
            pr = ac_annual / (poa_annual * system.module_parameters['pdc0'] / 1e6)
        else:
            pr = 0.0

        system_size_kw = system.module_parameters['pdc0'] / 1000
        capacity_factor = (
            ac_annual / (system_size_kw * 8760)
            if system_size_kw
            else 0.0
        )

        ghi_mean = _safe_float(weather['ghi'].mean()) if 'ghi' in weather else None
        dni_mean = _safe_float(weather['dni'].mean()) if 'dni' in weather else None
        dhi_mean = _safe_float(weather['dhi'].mean()) if 'dhi' in weather else None
        temp_mean = _safe_float(weather.get('temp_air').mean()) if 'temp_air' in weather else None
        wind_mean = _safe_float(weather.get('wind_speed').mean()) if 'wind_speed' in weather else None

        altitude = _safe_float(meta.get('altitude')) if isinstance(meta, dict) else None

        domains = {
            'solar_geometry': {
                'summary': (
                    "Efemérides solares derivadas da série NASA POWER, cobrindo "
                    f"{solar_hours} horários e suportando ajustes de tilt/azimute."
                ),
                'indicators': {
                    'latitude_deg': round(latitude, 6),
                    'longitude_deg': round(longitude, 6),
                    'array_tilt_deg': round(tilt, 2),
                    'array_azimuth_deg': round(azimuth, 2),
                    'altitude_m': altitude,
                    'sampled_hours': solar_hours,
                    'min_zenith_deg': _safe_float(min_zenith),
                    'max_elevation_deg': _safe_float(max_elevation),
                },
            },
            'radiometric_climate': {
                'summary': (
                    "Componentes GHI/DNI/DHI médios e condições atmosféricas "
                    "retiradas do dataset horário NASA POWER."
                ),
                'indicators': {
                    'mean_ghi_wm2': ghi_mean,
                    'mean_dni_wm2': dni_mean,
                    'mean_dhi_wm2': dhi_mean,
                    'mean_temp_c': temp_mean,
                    'mean_wind_ms': wind_mean,
                    'poa_model': 'haydavies',
                },
            },
            'pv_conversion': {
                'summary': (
                    "pvlib ModelChain (AOI físico, SAPM térmico, perdas pvwatts) "
                    "com montagem {mount}."
                ).format(mount=mount_type),
                'indicators': {
                    'system_loss_fraction': round(system_loss, 3),
                    'module_pdc0_kw': round(system.module_parameters['pdc0'] / 1000, 3),
                    'inverter_pdc0_kw': round(inverter_parameters['pdc0'] / 1000, 3),
                    'inverter_efficiency_nominal': inverter_parameters['eta_inv_nom'],
                },
            },
            'performance_analysis': {
                'summary': (
                    "Energia anual e KPIs ajustados para um ano completo para "
                    "alimentar Origination e MCP."
                ),
                'indicators': {
                    'annual_ac_kwh': round(ac_annual, 1),
                    'performance_ratio': round(pr, 3),
                    'capacity_factor': round(capacity_factor, 3),
                    'poa_annual_kwh_m2': _safe_float(poa_annual / 1000),
                    'expected_system_losses_pct': round(system_loss * 100, 1),
                    'scaling_factor': round(scaling_factor, 3),
                },
            },
        }

        return {
            'kwh_year': round(ac_annual, 1),
            'pr': round(pr, 3),
            'mc_result': {
                'poa_annual_kwh_m2': _safe_float(poa_annual / 1000),
                'system_size_kw': system_size_kw,
                'data_source': f"NASA POWER ({solar_hours} horas)",
                'mount_type': mount_type,
                'tilt': tilt,
                'azimuth': azimuth
            },
            'domains': domains,
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
        poa_annual *= scaling_factor

        # PR típico para sistema bem dimensionado
        pr = 0.80 * (1 - system_loss)

        solar_hours = len(times)
        min_zenith = _safe_float(solar_position['zenith'].min())
        max_elevation = _safe_float(solar_position['elevation'].max())

        domains = {
            'solar_geometry': {
                'summary': (
                    "Efemérides sintéticas (céu limpo) geradas a cada 12 h para "
                    "construir o quadro astronômico anual."
                ),
                'indicators': {
                    'latitude_deg': round(latitude, 6),
                    'longitude_deg': round(longitude, 6),
                    'array_tilt_deg': round(tilt, 2),
                    'array_azimuth_deg': round(azimuth, 2),
                    'sampled_hours': solar_hours,
                    'min_zenith_deg': min_zenith,
                    'max_elevation_deg': max_elevation,
                },
            },
            'radiometric_climate': {
                'summary': "Modelo Ineichen de céu limpo sem dados meteorológicos reais.",
                'indicators': {
                    'mean_ghi_wm2': _safe_float(clearsky['ghi'].mean()),
                    'mean_dni_wm2': _safe_float(clearsky['dni'].mean()),
                    'mean_dhi_wm2': _safe_float(clearsky['dhi'].mean()),
                    'poa_model': 'haydavies',
                },
            },
            'pv_conversion': {
                'summary': (
                    "Conversão PV simplificada (eficiência fixa 15% módulo, 96% inversor) "
                    "com perdas agregadas."
                ),
                'indicators': {
                    'system_loss_fraction': round(system_loss, 3),
                    'module_efficiency_assumed': 0.15,
                    'inverter_efficiency_assumed': 0.96,
                },
            },
            'performance_analysis': {
                'summary': (
                    "Energia anual estimada via clearsky para desbloquear recomendações "
                    "quando dados climáticos não estão disponíveis."
                ),
                'indicators': {
                    'annual_ac_kwh': round(kwh_annual, 1),
                    'performance_ratio': round(pr, 3),
                    'poa_annual_kwh_m2': _safe_float(poa_annual / 1000),
                    'expected_system_losses_pct': round(system_loss * 100, 1),
                    'scaling_factor': round(scaling_factor, 3),
                },
            },
        }

        return {
            'kwh_year': round(kwh_annual, 1),
            'pr': round(pr, 3),
            'mc_result': {
                'poa_annual_kwh_m2': _safe_float(poa_annual / 1000),
                'system_size_kw': 1.0,
                'data_source': "Clearsky Model",
                'mount_type': "fixed",
                'tilt': tilt,
                'azimuth': azimuth
            },
            'domains': domains,
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

    domains = {
        'solar_geometry': {
            'summary': (
                "Sem efemérides explícitas; utiliza apenas latitude/longitude para "
                "calcular heurísticas regionais."
            ),
            'indicators': {
                'latitude_deg': round(latitude, 6),
                'longitude_deg': round(longitude, 6),
            },
        },
        'radiometric_climate': {
            'summary': (
                "Horas de sol pleno estimadas por região ou média NASA POWER anual "
                "(fallback)."
            ),
            'indicators': {
                'hsp_hours_per_day': round(hsp, 2),
                'source': (
                    "regional_lookup" if insolation['is_estimated'] else "nasa_power_annual"
                ),
                'ghi_annual_kwh_m2': _safe_float(insolation.get('ghi_annual')),
                'dni_annual_kwh_m2': _safe_float(insolation.get('dni_annual')),
            },
        },
        'pv_conversion': {
            'summary': (
                "Modelo PVWatts agregado (1 kWp) com perdas sistêmicas médias "
                "para manter o ciclo MCP/AP2 em funcionamento."
            ),
            'indicators': {
                'system_loss_fraction': round(system_loss, 3),
                'module_reference_kw': 1.0,
            },
        },
        'performance_analysis': {
            'summary': (
                "Estimativa simplificada de produção anual e PR típico quando "
                "não há dados meteorológicos disponíveis."
            ),
            'indicators': {
                'annual_ac_kwh': round(kwh_per_kwp_year, 1),
                'performance_ratio': round(pr, 3),
                'expected_system_losses_pct': round(system_loss * 100, 1),
            },
        },
    }

    return {
        'kwh_year': round(kwh_per_kwp_year, 1),
        'pr': round(pr, 3),
        'mc_result': {
            'hsp': round(hsp, 2),
            'system_size_kw': 1.0,
            'data_source': "Simplified Estimate" if insolation['is_estimated'] else "NASA POWER Annual",
            'mount_type': "fixed",
            'tilt': "optimal",
            'azimuth': "optimal",
        },
        'domains': domains,
    }
