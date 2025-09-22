from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from gd_providers_api.main import app

client = TestClient(app)


def test_metadata_endpoint_returns_dataset_info() -> None:
    response = client.get("/metadata")
    assert response.status_code == 200
    payload = response.json()
    assert payload["api"] == "br.gd.providers"
    assert payload["version"] == "2025-09-20"
    assert payload["provider_count"] == 20


def test_list_providers_filters_by_state() -> None:
    response = client.get("/providers", params={"state": "RJ"})
    assert response.status_code == 200
    providers = response.json()
    assert any(provider["id"] == "enel-rj" for provider in providers)
    assert all("RJ" in provider["states"] for provider in providers)


def test_retrieve_specific_provider() -> None:
    response = client.get("/providers/neoenergia-coelba-ba")
    assert response.status_code == 200
    payload = response.json()
    assert payload["group"] == "Neoenergia"
    assert payload["submission"]["requirements"]["captcha"] is True


def test_submission_type_filter() -> None:
    response = client.get("/providers", params={"submission_type": "web_portal_docs"})
    assert response.status_code == 200
    providers = response.json()
    assert providers
    assert all(provider["submission"]["type"] == "web_portal_docs" for provider in providers)


def test_provider_not_found_returns_404() -> None:
    response = client.get("/providers/unknown-provider")
    assert response.status_code == 404
    assert response.json()["detail"] == "Provider not found"
