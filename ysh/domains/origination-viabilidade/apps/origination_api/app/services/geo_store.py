"""Persistence helpers for GeoJSON KPI features stored on disk.

The API endpoints can leverage these utilities to keep a lightweight cache of
all enriched leads under ``ysh/domains/origination-viabilidade/data``.  Keeping
an explicit representation on disk allows other processes (analytics notebooks,
data pipelines, etc.) to consume the same GeoJSON artefacts without reaching the
application database.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

DATA_ROOT = Path(__file__).resolve().parents[5] / "data"
GEOJSON_PATH = DATA_ROOT / "lead_geo_kpis.geojson"


def _empty_collection() -> dict[str, Any]:
    return {"type": "FeatureCollection", "features": []}


def load_feature_collection() -> dict[str, Any]:
    """Return the persisted FeatureCollection or an empty structure."""

    if GEOJSON_PATH.exists():
        with GEOJSON_PATH.open("r", encoding="utf-8") as fh:
            try:
                data = json.load(fh)
            except json.JSONDecodeError:
                data = _empty_collection()
            else:
                if not isinstance(data, dict) or data.get("type") != "FeatureCollection":
                    data = _empty_collection()
        return data
    return _empty_collection()


def write_feature_collection(collection: dict[str, Any]) -> None:
    """Persist ``collection`` ensuring the directory exists."""

    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    with GEOJSON_PATH.open("w", encoding="utf-8") as fh:
        json.dump(collection, fh, ensure_ascii=False, indent=2, sort_keys=True)


def _normalise_feature(feature: dict[str, Any], *, lead_id: str) -> dict[str, Any]:
    properties = dict(feature.get("properties") or {})
    properties.setdefault("lead_id", lead_id)
    feature = {
        "type": feature.get("type", "Feature"),
        "id": feature.get("id"),
        "geometry": feature.get("geometry"),
        "properties": properties,
    }
    return feature


def upsert_feature(*, feature: dict[str, Any], lead_id: str) -> dict[str, Any]:
    """Insert or update ``feature`` within the on-disk FeatureCollection."""

    collection = load_feature_collection()
    normalised = _normalise_feature(feature, lead_id=lead_id)
    features: list[dict[str, Any]] = list(collection.get("features") or [])

    updated = False
    for index, existing in enumerate(features):
        if existing.get("id") == normalised.get("id"):
            features[index] = normalised
            updated = True
            break
    if not updated:
        features.append(normalised)

    collection["features"] = features
    write_feature_collection(collection)
    return normalised


def get_feature_by_key(composite_key: str) -> dict[str, Any] | None:
    """Fetch a feature by its composite key (Feature ``id``)."""

    collection = load_feature_collection()
    for feature in collection.get("features", []):
        if feature.get("id") == composite_key:
            return feature
    return None


def find_features_by_coordinates(*, latitude: float, longitude: float) -> list[dict[str, Any]]:
    """Return features whose coordinates match ``latitude``/``longitude``."""

    lat_norm = round(float(latitude), 6)
    lon_norm = round(float(longitude), 6)

    matches: list[dict[str, Any]] = []
    for feature in load_feature_collection().get("features", []):
        try:
            lon, lat = feature["geometry"]["coordinates"]
        except (KeyError, TypeError, ValueError):
            continue
        if round(float(lat), 6) == lat_norm and round(float(lon), 6) == lon_norm:
            matches.append(feature)
    return matches


def features_for_leads(lead_ids: Iterable[str]) -> list[dict[str, Any]]:
    """Return all features that belong to ``lead_ids``."""

    lead_id_set = {str(lead_id) for lead_id in lead_ids}
    results: list[dict[str, Any]] = []
    for feature in load_feature_collection().get("features", []):
        properties = feature.get("properties", {})
        if str(properties.get("lead_id")) in lead_id_set:
            results.append(feature)
    return results


__all__ = [
    "DATA_ROOT",
    "GEOJSON_PATH",
    "find_features_by_coordinates",
    "features_for_leads",
    "get_feature_by_key",
    "load_feature_collection",
    "upsert_feature",
]
