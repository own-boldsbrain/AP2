"""Utilities for composing GeoJSON features enriched with regulatory KPIs.

The enrichment process consolidates KPIs from public data sources (BACEN, EPE,
ANEEL, IBGE and QUOD) into a single GeoJSON feature keyed by the tuple
``CPF + CEP + LAT + LNG``.  Keeping this logic in a dedicated module allows the
REST layer to remain thin while enabling unit tests to cover the geospatial
normalisation behaviour without the need for a database.
"""

from __future__ import annotations

from typing import Any, Mapping

import re

# The KPI providers we expect to receive for each enriched lead.  Keeping the
# list centralised makes it easy to extend in the future and avoids scattering
# literal strings across the codebase.
EXPECTED_KPI_KEYS = ("bacen", "epe", "aneel", "ibge", "quod")

_NUMERIC_PATTERN = re.compile(r"\D+")


def _sanitize_numeric(value: str | None) -> str:
    """Return only the numeric characters contained in ``value``."""

    if not value:
        return ""
    return _NUMERIC_PATTERN.sub("", value)


def _normalise_coordinate(value: float) -> float:
    """Round coordinates to six decimal places to stabilise the compound key."""

    return round(float(value), 6)


def build_geo_key(cpf: str, cep: str, latitude: float, longitude: float) -> str:
    """Compose a stable key using the CPF, CEP and geographic coordinates.

    The CPF and CEP are stripped from any punctuation so that ``123.456.789-00``
    and ``12345678900`` map to the same key.  Coordinates are rounded to reduce
    floating point noise and ensure that serialisations coming from different
    providers still collapse into the same identity.
    """

    cpf_clean = _sanitize_numeric(cpf)
    cep_clean = _sanitize_numeric(cep)
    lat = _normalise_coordinate(latitude)
    lon = _normalise_coordinate(longitude)
    return f"{cpf_clean}:{cep_clean}:{lat:.6f}:{lon:.6f}"


def ensure_kpi_payload(kpis: Mapping[str, Any] | None) -> dict[str, Any]:
    """Guarantee the presence of the expected KPI namespaces.

    Any missing namespace defaults to an empty mapping which simplifies the
    serialisation logic downstream and yields predictable schemas for the API
    consumer.
    """

    payload: dict[str, Any] = {name: {} for name in EXPECTED_KPI_KEYS}
    if not kpis:
        return payload
    for key, value in kpis.items():
        if key in payload and value is not None:
            payload[key] = value
    return payload


def build_geojson_feature(
    *,
    cpf: str,
    cep: str,
    latitude: float,
    longitude: float,
    kpis: Mapping[str, Any] | None = None,
    properties: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a GeoJSON feature embedding the KPI payload.

    Additional properties supplied by callers are merged with the core
    attributes (CPF, CEP and the KPI namespaces).  The feature ``id`` mirrors
    the compound key used in the database which helps clients correlate stored
    records with API responses.
    """

    kpi_payload = ensure_kpi_payload(kpis)
    cpf_clean = _sanitize_numeric(cpf)
    cep_clean = _sanitize_numeric(cep)
    base_properties: dict[str, Any] = {
        "cpf": cpf_clean,
        "cep": cep_clean,
        "kpis": kpi_payload,
    }
    if properties:
        base_properties.update(properties)
    return {
        "type": "Feature",
        "id": build_geo_key(cpf_clean, cep_clean, latitude, longitude),
        "geometry": {
            "type": "Point",
            "coordinates": [
                _normalise_coordinate(longitude),
                _normalise_coordinate(latitude),
            ],
        },
        "properties": base_properties,
    }


__all__ = [
    "EXPECTED_KPI_KEYS",
    "build_geo_key",
    "build_geojson_feature",
    "ensure_kpi_payload",
]
