"""Tests for the NATS helper utilities."""

import json

import pytest

from app.events import nats_bus


class _DummyNC:
    def __init__(self) -> None:
        self.published: list[tuple[str, bytes]] = []

    async def publish(self, subject: str, data: bytes) -> None:
        self.published.append((subject, data))


@pytest.mark.asyncio
async def test_publish_completed_returns_true_when_connected(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy = _DummyNC()
    monkeypatch.setattr(nats_bus, "nc", dummy, raising=False)

    payload = {"lead_id": "123", "result": "ok"}
    assert await nats_bus.publish_completed(payload) is True
    assert dummy.published == [
        (nats_bus.SUBJECT_COMPLETED, json.dumps(payload).encode()),
    ]


@pytest.mark.asyncio
async def test_publish_completed_returns_false_without_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(nats_bus, "nc", None, raising=False)

    assert await nats_bus.publish_completed({"lead_id": "missing"}) is False
