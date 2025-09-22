from pydantic import BaseModel
from math import isnan

class ViabilityIn(BaseModel):
    lat: float
    lon: float
    tilt_deg: float = 20
    azimuth_deg: float = 180
    mount_type: str = "fixed"
    system_loss_fraction: float = 0.14
    meteo_source: str = "NASA_POWER"  # ou "CLEARSKY_ONLY"

class ViabilityOut(BaseModel):
    kwh_year: float
    pr: float
    mc_result: dict | None = None

def compute_viability(inp: ViabilityIn) -> ViabilityOut:
    # MVP: usa média HSP de 5.0h/dia se não houver meteo externo.
    HSP = 5.0
    PR = 0.80
    losses = inp.system_loss_fraction
    # Considera 1 kWp base e retorna kWh/kWp/ano ~ HSP*365*PR*(1-losses)
    kwh_per_kwp_year = HSP * 365 * PR * (1 - losses)
    # Retorna por kWp; o sizing final determinará kWp
    return ViabilityOut(kwh_year=round(kwh_per_kwp_year, 1), pr=round(PR*(1-losses), 3))