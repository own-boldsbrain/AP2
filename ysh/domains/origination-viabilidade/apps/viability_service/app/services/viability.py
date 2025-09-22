"""Core viability calculations exposed by the viability service.

The service intentionally keeps the public surface area extremely small: a
single ``compute_viability`` function that transforms validated ``ViabilityIn``
inputs into a ``ViabilityOut`` payload.  The heavy lifting is delegated to the
``app.meteo.pv_system`` module which abstracts the interaction with pvlib and
fallback heuristics when pvlib or NASA POWER data are not available.
"""

from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, Field

from app.meteo.pv_system import estimate_pv_performance


class ViabilityIn(BaseModel):
    """Input payload accepted by ``/tools/viability.compute``.

    Attributes
    ----------
    lat / lon
        Geographic coordinates in decimal degrees.
    tilt_deg / azimuth_deg
        Plane-of-array configuration.  Defaults align with common residential
        rooftops in Brazil.
    mount_type
        ``"fixed"`` or ``"single_axis_tracker"``.  Only used for metadata at the
        moment but kept to future-proof the API contract.
    system_loss_fraction
        Aggregated losses (soiling, wiring, mismatch …) expressed as a fraction
        between ``0`` and ``1``.
    meteo_source
        Optional override to force ``"CLEARSKY_ONLY"`` estimations when an
        online NASA POWER query is not desired.
    """

    lat: float
    lon: float
    tilt_deg: float = Field(default=20, ge=0, le=90)
    azimuth_deg: float = Field(default=180, ge=0, le=360)
    mount_type: str = Field(default="fixed")
    system_loss_fraction: float = Field(default=0.14, ge=0, lt=1)
    meteo_source: str = Field(default="NASA_POWER")


class ViabilityOut(BaseModel):
    """Result produced by ``compute_viability``."""

    kwh_year: float = Field(description="Expected annual AC energy for 1 kWp")
    pr: float = Field(description="Performance Ratio of the simulated system")
    mc_result: Dict[str, Any] | None = Field(
        default=None,
        description="Raw metadata emitted by the model chain (if available).",
    )


def compute_viability(inp: ViabilityIn) -> ViabilityOut:
    """Compute photovoltaic viability for a canonical 1 kWp system.

    The helper gracefully handles environments where pvlib is unavailable by
    falling back to deterministic heuristics defined in
    :func:`app.meteo.pv_system.estimate_pv_performance`.
    """

    result = estimate_pv_performance(
        latitude=inp.lat,
        longitude=inp.lon,
        tilt=inp.tilt_deg,
        azimuth=inp.azimuth_deg,
        mount_type=inp.mount_type,
        system_loss=inp.system_loss_fraction,
        meteo_source=inp.meteo_source,
    )

    return ViabilityOut(**result)
