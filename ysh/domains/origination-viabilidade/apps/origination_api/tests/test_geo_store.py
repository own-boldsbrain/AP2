from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services import geo_store


@pytest.fixture(autouse=True)
def _isolate_geo_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    data_root = tmp_path / "data"
    monkeypatch.setattr(geo_store, "DATA_ROOT", data_root)
    monkeypatch.setattr(geo_store, "GEOJSON_PATH", data_root / "lead_geo_kpis.geojson")
    yield


def test_upsert_feature_creates_file(tmp_path: Path):
    feature = {
        "type": "Feature",
        "id": "12345678900:01310000:-23.561230:-46.655100",
        "geometry": {"type": "Point", "coordinates": [-46.6551, -23.56123]},
        "properties": {
            "cpf": "12345678900",
            "cep": "01310000",
            "kpis": {"bacen": {"selic": 0.1}},
        },
    }

    stored = geo_store.upsert_feature(feature=feature, lead_id="lead-1")
    assert stored["properties"]["lead_id"] == "lead-1"

    with geo_store.GEOJSON_PATH.open() as fh:
        payload = json.load(fh)
    assert payload["type"] == "FeatureCollection"
    assert payload["features"][0]["id"] == feature["id"]


def test_find_features_by_coordinates_filters(tmp_path: Path):
    feature = {
        "type": "Feature",
        "id": "12345678900:01310000:-23.561230:-46.655100",
        "geometry": {"type": "Point", "coordinates": [-46.6551, -23.56123]},
        "properties": {"lead_id": "lead-1"},
    }
    geo_store.upsert_feature(feature=feature, lead_id="lead-1")

    matches = geo_store.find_features_by_coordinates(
        latitude=-23.56123, longitude=-46.6551
    )
    assert len(matches) == 1
    assert matches[0]["id"] == feature["id"]
