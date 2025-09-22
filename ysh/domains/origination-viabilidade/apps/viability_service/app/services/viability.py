from math import isnan
from typing import Any, Dict, Optional

from app.meteo.pv_system import estimate_pv_performance
from pydantic import BaseModel


class ViabilityIn(BaseModel):
    lat: float
    lon: float
    tilt_deg: float = 20
    azimuth_deg: float = 180
    mount_type: str = 'fixed'
    system_loss_fraction: float = 0.14
    meteo_source: str = 'NASA_POWER'  # ou "CLEARSKY_ONLY"


class ViabilityOut(BaseModel):
    kwh_year: float
    pr: float
    mc_result: Dict[str, Any] | None = None


def compute_viability(inp: ViabilityIn) -> ViabilityOut:
    """
    Computa a viabilidade energética de um sistema fotovoltaico.

    Utiliza o pvlib e dados NASA POWER para calcular a geração anual
    e o Performance Ratio (PR) para um sistema de 1kWp.
    """
    # Chama o módulo pv_system para estimativa completa
    result = estimate_pv_performance(
        latitude=inp.lat,
        longitude=inp.lon,
        tilt=inp.tilt_deg,
        azimuth=inp.azimuth_deg,
        mount_type=inp.mount_type,
        system_loss=inp.system_loss_fraction,
        meteo_source=inp.meteo_source,
    )

    # Converte o resultado para o formato de saída
    return ViabilityOut(
        kwh_year=result['kwh_year'],
        pr=result['pr'],
        mc_result=result['mc_result'],
    )
