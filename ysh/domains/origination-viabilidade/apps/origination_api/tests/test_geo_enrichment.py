from app.services.geo_enrichment import (
    build_geo_key,
    build_geojson_feature,
    ensure_kpi_payload,
)


def test_build_geo_key_normalises_inputs() -> None:
    key = build_geo_key("123.456.789-00", "01310-000", -23.56123, -46.6551)
    assert key == "12345678900:01310000:-23.561230:-46.655100"


def test_ensure_kpi_payload_fills_missing_namespaces() -> None:
    payload = ensure_kpi_payload({"bacen": {"selic": 0.1}, "ibge": None})
    assert set(payload.keys()) == {"bacen", "epe", "aneel", "ibge", "quod"}
    assert payload["bacen"] == {"selic": 0.1}
    assert payload["epe"] == {}
    assert payload["ibge"] == {}


def test_build_geojson_feature_embeds_kpis_and_properties() -> None:
    feature = build_geojson_feature(
        cpf="987.654.321-00",
        cep="22071-060",
        latitude=-22.971177,
        longitude=-43.182543,
        kpis={"aneel": {"distributor": "LIGHT"}},
        properties={"segment": "residential"},
    )

    assert feature["type"] == "Feature"
    assert feature["geometry"] == {
        "type": "Point",
        "coordinates": [-43.182543, -22.971177],
    }
    assert feature["properties"]["cpf"] == "98765432100"
    assert feature["properties"]["cep"] == "22071060"
    assert feature["properties"]["segment"] == "residential"
    assert feature["properties"]["kpis"]["aneel"] == {"distributor": "LIGHT"}
