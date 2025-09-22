from typing import Any, Dict, List

import httpx
import pytest

from ..agent import PREOrchestratorAgent, TIER_FACTORS


class DummyResponse:
    def __init__(self, payload: Dict[str, Any], status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def json(self) -> Dict[str, Any]:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPError("error")


class DummyHTTPClient:
    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []
        self._response: DummyResponse | None = None
        self._error: Exception | None = None

    def queue_response(self, payload: Dict[str, Any], status_code: int = 200) -> None:
        self._response = DummyResponse(payload, status_code)
        self._error = None

    def queue_error(self, error: Exception) -> None:
        self._response = None
        self._error = error

    async def post(self, url: str, json: Dict[str, Any] | None = None) -> DummyResponse:
        self.calls.append({"url": url, "json": json})
        if self._error:
            raise self._error
        if not self._response:
            raise RuntimeError("No response queued")
        return self._response

    async def aclose(self) -> None:  # pragma: no cover - noop for tests
        return None


class DummyNATS:
    def __init__(self) -> None:
        self.messages: List[tuple[str, bytes]] = []
        self.is_closed = False

    async def connect(self, url: str) -> None:  # pragma: no cover - connection is trivial in tests
        self.is_closed = False

    async def close(self) -> None:  # pragma: no cover - noop
        self.is_closed = True

    async def publish(self, subject: str, payload: bytes) -> None:
        self.messages.append((subject, payload))


@pytest.mark.asyncio
async def test_size_system_computes_band_and_tier() -> None:
    client = DummyHTTPClient()
    agent = PREOrchestratorAgent(http_client=client, nats_client=DummyNATS())
    sizing = agent.size_system(
        annual_consumption_kwh=7200,
        kwh_per_kwp_year=1300,
        tier_factor=TIER_FACTORS["T130"],
    )
    assert sizing["tier_code"] == "T130"
    assert sizing["band_code"] in {"M", "L"}
    assert sizing["kwp"] > 0


@pytest.mark.asyncio
async def test_determine_modality_rules() -> None:
    agent = PREOrchestratorAgent(http_client=DummyHTTPClient(), nats_client=DummyNATS())
    assert await agent.determine_modality("RESIDENCIAL", True, False) == "AUTO_LOCAL"
    assert await agent.determine_modality("COND_MUC", True, False) == "MUC"
    assert await agent.determine_modality("RESIDENCIAL", False, False) == "COMPARTILHADA"
    assert await agent.determine_modality("RESIDENCIAL", True, True) == "AUTO_REMOTO"


@pytest.mark.asyncio
async def test_generate_recommendations_fallback() -> None:
    client = DummyHTTPClient()
    client.queue_error(httpx.HTTPError("boom"))
    agent = PREOrchestratorAgent(http_client=client, nats_client=DummyNATS())
    offers = await agent.generate_recommendations("lead-123", {"band_code": "M", "kwp": 8.0, "expected_kwh_year": 9500})
    assert len(offers["offers"]) == 3
    for offer in offers["offers"]:
        assert offer["sku"].startswith("M-")


@pytest.mark.asyncio
async def test_emit_event_uses_nats() -> None:
    client = DummyHTTPClient()
    nats_client = DummyNATS()
    agent = PREOrchestratorAgent(http_client=client, nats_client=nats_client)
    await agent.emit_event("test.event", {"foo": "bar"})
    assert nats_client.messages
    subject, payload = nats_client.messages[0]
    assert subject == "ysh.origination.test.event"
    assert b"foo" in payload

    await agent.close()
