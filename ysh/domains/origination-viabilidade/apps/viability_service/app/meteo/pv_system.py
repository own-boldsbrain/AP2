"""Deterministic photovoltaic performance estimations.

The module favours graceful degradation so that unit tests run without the
heavy ``pvlib`` dependency or external network calls.  When pvlib is available
we execute a lightweight ModelChain fed by NASA POWER data.  Otherwise the
functions fall back to analytical heuristics derived from Brazilian solar
atlases.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

import pandas as pd

try:  # pragma: no cover - pvlib is optional in the execution environment
    import pvlib
    from pvlib import location, modelchain, pvsystem
except ImportError:  # pragma: no cover - executed when pvlib is missing
    pvlib = None  # type: ignore[assignment]

from app.meteo.nasa_power import get_annual_insolation, get_nasa_power


def estimate_pv_performance(
    *,
    latitude: float,
    longitude: float,
    tilt: float = 20,
    azimuth: float = 180,
    mount_type: str = "fixed",
    system_loss: float = 0.14,
    meteo_source: str = "NASA_POWER",
) -> Dict[str, Any]:
    """Estimate annual production for a canonical 1 kWp PV system."""

    # Hemispheric adjustment: for locations in the southern hemisphere the
    # optimal azimuth is north (0°).
    if latitude < 0 and azimuth == 180:
        azimuth = 0

    if pvlib is None:
        return simplified_estimate(latitude=latitude, longitude=longitude, system_loss=system_loss)

    try:
        if meteo_source == "CLEARSKY_ONLY":
            return clearsky_estimate(latitude=latitude, longitude=longitude, tilt=tilt, azimuth=azimuth, system_loss=system_loss)

        end = datetime.utcnow()
        start = datetime(end.year, 1, 1)
        weather, meta = get_nasa_power(latitude, longitude, start, end)
        if weather.empty:
            return clearsky_estimate(latitude=latitude, longitude=longitude, tilt=tilt, azimuth=azimuth, system_loss=system_loss)

        loc = location.Location(latitude, longitude, tz="UTC", altitude=meta.get("altitude", 0))
        system = pvsystem.PVSystem(
            surface_tilt=tilt,
            surface_azimuth=azimuth,
            module_parameters={"pdc0": 1000, "gamma_pdc": -0.004},
            inverter_parameters={"pdc0": 1100, "eta_inv_nom": 0.96},
            losses_parameters={"dc_ohmic_percent": system_loss * 100},
        )

        mc = modelchain.ModelChain(
            system,
            loc,
            aoi_model="physical",
            spectral_model="no_loss",
            temperature_model="sapm",
            losses_model="pvwatts",
        )
        mc.run_model(weather)

        ac_energy = mc.results.ac.sum() / 1000.0
        poa_annual = mc.results.total_irrad["poa_global"].sum()
        scaling_factor = 1.0
        hours_in_data = len(weather)
        if hours_in_data and hours_in_data < 8760:
            scaling_factor = 8760 / hours_in_data
            ac_energy *= scaling_factor
            poa_annual *= scaling_factor

        pr = ac_energy / (poa_annual / 1000.0) if poa_annual else 0.75
        return {
            "kwh_year": round(ac_energy, 1),
            "pr": round(pr, 3),
            "mc_result": {
                "poa_annual": round(poa_annual, 1),
                "system_size_kw": 1.0,
                "data_source": f"NASA POWER ({hours_in_data}h)",
                "mount_type": mount_type,
                "tilt": tilt,
                "azimuth": azimuth,
            },
        }
    except Exception:  # pragma: no cover - any runtime error falls back to heuristics
        return simplified_estimate(latitude=latitude, longitude=longitude, system_loss=system_loss)


def clearsky_estimate(*, latitude: float, longitude: float, tilt: float, azimuth: float, system_loss: float) -> Dict[str, Any]:
    """Estimate production using pvlib clear-sky models only."""

    if pvlib is None:  # pragma: no cover - only executed without pvlib
        return simplified_estimate(latitude=latitude, longitude=longitude, system_loss=system_loss)

    loc = location.Location(latitude, longitude, tz="UTC")
    times = pd.date_range(start=f"{datetime.utcnow().year}-01-01", end=f"{datetime.utcnow().year}-12-31 23:00:00", freq="3H", tz="UTC")
    solar_position = loc.get_solarposition(times)
    clearsky = loc.get_clearsky(times)
    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        solar_zenith=solar_position["zenith"],
        solar_azimuth=solar_position["azimuth"],
        dni=clearsky["dni"],
        ghi=clearsky["ghi"],
        dhi=clearsky["dhi"],
        model="haydavies",
    )

    poa_annual = float(poa["poa_global"].sum())
    scaling_factor = 8760 / len(times) if len(times) else 1.0
    poa_annual *= scaling_factor

    efficiency = 0.15 * 0.96 * (1 - system_loss)
    kwh_year = poa_annual * efficiency / 1000.0
    pr = 0.80 * (1 - system_loss)

    return {
        "kwh_year": round(kwh_year, 1),
        "pr": round(pr, 3),
        "mc_result": {
            "poa_annual": round(poa_annual, 1),
            "system_size_kw": 1.0,
            "data_source": "pvlib clearsky",
            "mount_type": "fixed",
            "tilt": tilt,
            "azimuth": azimuth,
        },
    }


def simplified_estimate(*, latitude: float, longitude: float, system_loss: float) -> Dict[str, Any]:
    """Fallback deterministic estimation when no meteorological data exist."""

    insolation = get_annual_insolation(latitude, longitude)
    if insolation.get("is_estimated"):
        if -30 <= latitude <= -10 and -60 <= longitude <= -40:
            hsp = 4.8
        elif -10 <= latitude <= 0 and -70 <= longitude <= -35:
            hsp = 5.5
        elif 0 <= latitude <= 5 and -70 <= longitude <= -45:
            hsp = 5.2
        else:
            hsp = 5.0
    else:
        hsp = float(insolation["ghi_annual"]) / 365.0

    pr = 0.80 * (1 - system_loss)
    kwh_year = hsp * 365 * pr

    return {
        "kwh_year": round(kwh_year, 1),
        "pr": round(pr, 3),
        "mc_result": {
            "hsp": round(hsp, 2),
            "system_size_kw": 1.0,
            "data_source": "Simplified Estimate" if insolation.get("is_estimated") else "NASA POWER Annual",
            "mount_type": "fixed",
            "tilt": "optimal",
            "azimuth": "optimal",
        },
    }
