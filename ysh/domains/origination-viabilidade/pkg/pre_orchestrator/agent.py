"""Autonomous agent orchestrating the PRE (lead → viability → proposal) flow."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from httpx import HTTPError
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrNoServers, ErrTimeout

logger = logging.getLogger("pre_orchestrator")

ORIGINATION_API_URL = os.getenv("ORIGINATION_API_URL", "http://origination_api:8000")
VIABILITY_SERVICE_URL = os.getenv("VIABILITY_SERVICE_URL", "http://viability_service:8010")
ANEEL_TARIFFS_URL = os.getenv("ANEEL_TARIFFS_URL", "http://aneel_tariffs:8011")
NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")

DEFAULT_HSP = 5.0
DEFAULT_TARIFF_CENTS_PER_KWH = 120.0
DEFAULT_LOSSES = 0.14
DEFAULT_PR = 0.80

TIER_FACTORS = {"T115": 1.15, "T130": 1.30, "T145": 1.45, "T160": 1.60}
BAND_RANGES = {
    "XPP": (0, 0.5),
    "XS": (0.5, 3),
    "S": (3, 6),
    "M": (6, 12),
    "L": (12, 30),
    "XL": (30, 75),
    "XG": (75, 300),
    "XGG": (300, 1500),
}


class PREOrchestratorAgent:
    """Coordinator responsible for chaining the PRE blueprint end-to-end."""

    def __init__(
        self,
        *,
        http_client: httpx.AsyncClient | None = None,
        nats_client: NATS | None = None,
        origination_api_url: str = ORIGINATION_API_URL,
        viability_service_url: str = VIABILITY_SERVICE_URL,
        aneel_tariffs_url: str = ANEEL_TARIFFS_URL,
    ) -> None:
        self.http_client = http_client or httpx.AsyncClient(timeout=10.0)
        self._owns_http_client = http_client is None
        self.nats_client = nats_client or NATS()
        self._owns_nats_client = nats_client is None
        self.origination_api_url = origination_api_url.rstrip("/")
        self.viability_service_url = viability_service_url.rstrip("/")
        self.aneel_tariffs_url = aneel_tariffs_url.rstrip("/")
        self._nats_connected = False

    async def connect_nats(self) -> None:
        if self._nats_connected:
            return
        try:
            await self.nats_client.connect(NATS_URL)
            self._nats_connected = True
            logger.info("Connected to NATS")
        except (ErrNoServers, ErrConnectionClosed) as exc:  # pragma: no cover - network
            logger.error("Failed to connect to NATS: %s", exc)
            raise

    async def disconnect_nats(self) -> None:
        if not self._nats_connected:
            return
        await self.nats_client.close()
        self._nats_connected = False
        logger.info("Disconnected from NATS")

    async def create_update_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        if not lead_data.get("consent"):
            raise ValueError("Consentimento LGPD é obrigatório.")

        payload = lead_data.copy()
        if "cep" in payload and isinstance(payload["cep"], str):
            payload["cep"] = payload["cep"].replace("-", "").strip()
        if "uf" in payload and isinstance(payload["uf"], str):
            payload["uf"] = payload["uf"].strip().upper()

        url = f"{self.origination_api_url}/v1/leads"
        response = await self.http_client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    async def classify_consumer(self, lead_id: str, classification: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.origination_api_url}/v1/leads/{lead_id}/classify"
        response = await self.http_client.post(url, json=classification)
        response.raise_for_status()
        return response.json()

    async def select_modality(self, lead_id: str, modality: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.origination_api_url}/v1/leads/{lead_id}/modality"
        response = await self.http_client.post(url, json=modality)
        response.raise_for_status()
        return response.json()

    async def calculate_viability(self, viability_data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.viability_service_url}/tools/viability.compute"
        response = await self.http_client.post(url, json=viability_data)
        response.raise_for_status()
        return response.json()

    async def get_tariff_profile(self, tariff_data: Dict[str, Any]) -> Dict[str, Any]:
        components_url = f"{self.aneel_tariffs_url}/tools/aneel.tariffs.components.fetch"
        profile_url = f"{self.aneel_tariffs_url}/tools/aneel.tariffs.profile.build"
        try:
            comp_resp = await self.http_client.post(components_url, json=tariff_data)
            comp_resp.raise_for_status()
            rows = comp_resp.json().get("rows", [])
            profile_resp = await self.http_client.post(profile_url, json={"rows": rows})
            profile_resp.raise_for_status()
            return profile_resp.json()
        except HTTPError:
            logger.warning("Falling back to default tariff profile")
            return {"tariff_profile": {"cents_per_kwh": DEFAULT_TARIFF_CENTS_PER_KWH}}

    async def evaluate_economics(self, economics_data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.viability_service_url}/tools/economics.evaluate"
        response = await self.http_client.post(url, json=economics_data)
        response.raise_for_status()
        return response.json()

    def size_system(
        self,
        *,
        annual_consumption_kwh: float,
        kwh_per_kwp_year: float,
        tier_factor: float,
    ) -> Dict[str, Any]:
        base_generation = max(kwh_per_kwp_year, 1.0)
        kwp = (annual_consumption_kwh * tier_factor) / base_generation
        expected_kwh_year = kwp * base_generation
        band_code = self._detect_band(kwp)
        tier_code = self._detect_tier(tier_factor)
        return {
            "tier_code": tier_code,
            "band_code": band_code,
            "kwp": round(kwp, 2),
            "expected_kwh_year": round(expected_kwh_year, 0),
        }

    def _detect_band(self, kwp: float) -> str:
        for band, (lower, upper) in BAND_RANGES.items():
            if lower <= kwp < upper:
                return band
        return "XGG"

    def _detect_tier(self, tier_factor: float) -> str:
        for tier, factor in TIER_FACTORS.items():
            if abs(factor - tier_factor) < 1e-2:
                return tier
        return "T115"

    async def generate_recommendations(self, lead_id: str, reco_data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.origination_api_url}/v1/leads/{lead_id}/recommendations"
        try:
            response = await self.http_client.post(url, json=reco_data)
            response.raise_for_status()
            return response.json()
        except HTTPError:
            logger.warning("Falling back to offline recommendation builder")
            return {"offers": self._create_offers(reco_data)}

    def _create_offers(self, sizing: Dict[str, Any]) -> List[Dict[str, Any]]:
        band_code = sizing.get("band_code", "M")
        kwp = float(sizing.get("kwp", 6.0))
        expected_kwh_year = float(sizing.get("expected_kwh_year", kwp * 1200))
        upsell = self._upsell_rules(band_code)
        base_price = 7000
        return [
            {
                "sku": f"{band_code}-BASE",
                "title": f"Kit {band_code} Base",
                "capex_estimate": round(kwp * base_price, 2),
                "payback_estimate": 6.0,
                "upsell": upsell["base"],
            },
            {
                "sku": f"{band_code}-PLUS",
                "title": f"Kit {band_code} Plus",
                "capex_estimate": round(kwp * base_price * 1.1, 2),
                "payback_estimate": 5.5,
                "upsell": upsell["plus"],
            },
            {
                "sku": f"{band_code}-PRO",
                "title": f"Kit {band_code} Pro",
                "capex_estimate": round(kwp * base_price * 1.2, 2),
                "payback_estimate": 5.0,
                "upsell": upsell["pro"],
            },
        ]

    def _upsell_rules(self, band_code: str) -> Dict[str, List[str]]:
        if band_code in {"XPP", "XS", "S"}:
            return {
                "base": ["BATERIA_LIGHT", "INSURANCE_BASIC"],
                "plus": ["BATERIA_LIGHT", "INSURANCE_BASIC", "O&M_BASIC"],
                "pro": ["BATERIA_STD", "INSURANCE_STD", "O&M_BASIC"],
            }
        if band_code in {"M", "L"}:
            return {
                "base": ["BATERIA_STD", "DSM_TOU"],
                "plus": ["BATERIA_STD", "INSURANCE_STD", "O&M_STD"],
                "pro": ["BATERIA_PRO", "INSURANCE_STD", "O&M_STD"],
            }
        return {
            "base": ["O&M_STD", "INSURANCE_STD"],
            "plus": ["O&M_PRO", "INSURANCE_PREMIUM"],
            "pro": ["O&M_PRO", "INSURANCE_PREMIUM", "MONITORING_ADVANCED"],
        }

    async def emit_event(self, event_suffix: str, payload: Dict[str, Any]) -> None:
        if not self._nats_connected:
            try:
                await self.connect_nats()
            except Exception:
                return

        subject = f"ysh.origination.{event_suffix}"
        enriched = payload | {"timestamp": datetime.utcnow().isoformat()}
        try:
            await self.nats_client.publish(subject, json.dumps(enriched).encode("utf-8"))
        except (ErrConnectionClosed, ErrTimeout):  # pragma: no cover - network
            await asyncio.sleep(0)

    async def determine_modality(self, uc_type: str, has_roof: bool, multiple_ucs: bool) -> str:
        if has_roof and not multiple_ucs and uc_type != "COND_MUC":
            return "AUTO_LOCAL"
        if not has_roof or uc_type == "COND_MUC":
            return "MUC" if uc_type == "COND_MUC" else "COMPARTILHADA"
        if multiple_ucs:
            return "AUTO_REMOTO"
        return "AUTO_LOCAL"

    async def orchestrate_pre_process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        start = time.perf_counter()
        trace_id = str(uuid.uuid4())
        telemetry: Dict[str, Dict[str, float] | Dict[str, int]] = {
            "durations_ms": {},
            "retries": {"http": 0, "events": 0},
        }
        logs: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        final_bundle: Dict[str, Any] = {}

        try:
            lead_data = input_data.get("lead_data", {})
            consumption = input_data.get("consumption_data", {})
            preferences = input_data.get("preferences", {})
            classification_payload = {
                "tariff_group": input_data.get("tariff_group", "B1"),
                "consumer_class": input_data.get("consumer_class", "RESIDENCIAL"),
                "consumer_subclass": input_data.get("consumer_subclass"),
                "uc_type": input_data.get("uc_type", "RESIDENCIAL"),
            }

            capture_start = time.perf_counter()
            lead_resp = await self.create_update_lead(lead_data)
            lead_id = lead_resp.get("lead_id", lead_data.get("lead_id"))
            logs.append({"level": "INFO", "at": datetime.utcnow().isoformat(), "msg": "lead.created"})
            await self.emit_event("lead.captured.v1", {"lead_id": lead_id, "consent": lead_data.get("consent", False)})
            telemetry["durations_ms"]["capture"] = round((time.perf_counter() - capture_start) * 1000, 2)

            class_resp = await self.classify_consumer(lead_id, classification_payload)

            modality_start = time.perf_counter()
            modality = await self.determine_modality(
                class_resp.get("uc_type", classification_payload["uc_type"]),
                preferences.get("has_roof", True),
                preferences.get("multiple_ucs", False),
            )
            modality_payload = {
                "generation_modality": modality,
                "principal_uc": preferences.get("principal_uc"),
                "members": preferences.get("members", []),
            }
            await self.select_modality(lead_id, modality_payload)
            await self.emit_event("generation.modality.selected.v1", {"lead_id": lead_id, "generation_modality": modality})
            telemetry["durations_ms"]["modality"] = round((time.perf_counter() - modality_start) * 1000, 2)

            viability_start = time.perf_counter()
            viability_input = {
                "lat": lead_data.get("lat") or preferences.get("lat"),
                "lon": lead_data.get("lon") or preferences.get("lon"),
                "tilt_deg": preferences.get("tilt_deg", 20),
                "azimuth_deg": preferences.get("azimuth_deg", 180),
                "mount_type": preferences.get("mount_type", "fixed"),
                "system_loss_fraction": preferences.get("system_loss_fraction", DEFAULT_LOSSES),
                "meteo_source": preferences.get("meteo_source", "NASA_POWER"),
            }
            await self.emit_event("viability.requested.v1", {"lead_id": lead_id, "params": viability_input})
            viability_resp = await self.calculate_viability(viability_input)
            telemetry["durations_ms"]["viability"] = round((time.perf_counter() - viability_start) * 1000, 2)
            await self.emit_event(
                "viability.completed.v1",
                {
                    "lead_id": lead_id,
                    "kwh_year": viability_resp.get("kwh_year"),
                    "pr": viability_resp.get("pr"),
                },
            )
            logs.append({"level": "INFO", "at": datetime.utcnow().isoformat(), "msg": "viability.ok"})

            tariffs_start = time.perf_counter()
            tariff_profile = await self.get_tariff_profile({k: v for k, v in classification_payload.items() if v})
            telemetry["durations_ms"]["tariffs"] = round((time.perf_counter() - tariffs_start) * 1000, 2)

            economics_start = time.perf_counter()
            kwh_per_kwp_year = float(viability_resp.get("kwh_year", DEFAULT_HSP * 365 * DEFAULT_PR))
            annual_consumption = float(consumption.get("consumo_12m_kwh", 6000.0))
            preferred_tier = preferences.get("preferred_tier", "T115")
            tier_factor = TIER_FACTORS.get(preferred_tier, TIER_FACTORS["T115"])
            sizing = self.size_system(
                annual_consumption_kwh=annual_consumption,
                kwh_per_kwp_year=kwh_per_kwp_year,
                tier_factor=tier_factor,
            )
            economics_payload = {
                "kwh_year": sizing["expected_kwh_year"],
                "tariff_profile": tariff_profile.get("tariff_profile", {}),
                "capex": sizing["kwp"] * 6000,
                "opex": 0.02 * sizing["kwp"] * 6000,
            }
            economics_resp = await self.evaluate_economics(economics_payload)
            telemetry["durations_ms"]["economics"] = round((time.perf_counter() - economics_start) * 1000, 2)
            logs.append({"level": "INFO", "at": datetime.utcnow().isoformat(), "msg": "economics.ok"})

            sizing_start = time.perf_counter()
            reco_payload = {
                "preferred_tier": preferred_tier,
                "tier_code": sizing["tier_code"],
                "band_code": sizing["band_code"],
                "kwp": sizing["kwp"],
                "expected_kwh_year": sizing["expected_kwh_year"],
            }
            recommendations = await self.generate_recommendations(lead_id, reco_payload)
            await self.emit_event(
                "system.sized.v1",
                {
                    "lead_id": lead_id,
                    "kwp": sizing["kwp"],
                    "tier_code": sizing["tier_code"],
                    "band_code": sizing["band_code"],
                    "expected_kwh_year": sizing["expected_kwh_year"],
                },
            )
            await self.emit_event(
                "recommendation.bundle.created.v1",
                {
                    "lead_id": lead_id,
                    "offers_count": len(recommendations.get("offers", [])),
                    "tier_code": sizing["tier_code"],
                    "band_code": sizing["band_code"],
                },
            )
            telemetry["durations_ms"]["sizing_reco"] = round((time.perf_counter() - sizing_start) * 1000, 2)
            logs.append({"level": "INFO", "at": datetime.utcnow().isoformat(), "msg": "bundle.created"})

            final_bundle = {
                "lead_id": lead_id,
                "classification": {
                    "tariff_group": classification_payload["tariff_group"],
                    "consumer_class": classification_payload["consumer_class"],
                    "consumer_subclass": classification_payload.get("consumer_subclass"),
                    "uc_type": classification_payload["uc_type"],
                    "generation_modality": modality,
                },
                "viability": viability_resp,
                "economics": economics_resp,
                "sizing": sizing,
                "offers": recommendations.get("offers", []),
                "events_emitted": [
                    "lead.captured.v1",
                    "generation.modality.selected.v1",
                    "viability.requested.v1",
                    "viability.completed.v1",
                    "system.sized.v1",
                    "recommendation.bundle.created.v1",
                ],
            }
        except Exception as exc:  # pragma: no cover - orchestrator level guard
            logger.exception("Error while orchestrating PRE flow")
            errors.append({"level": "ERROR", "at": datetime.utcnow().isoformat(), "msg": str(exc)})

        telemetry["durations_ms"]["total"] = round((time.perf_counter() - start) * 1000, 2)
        return {
            "trace_id": trace_id,
            "inputs_digest": "sha256-placeholder",
            "final_bundle": final_bundle,
            "telemetry": telemetry,
            "logs": logs,
            "errors": errors,
        }

    async def close(self) -> None:
        if self._owns_http_client:
            await self.http_client.aclose()
        if self._owns_nats_client:
            await self.disconnect_nats()
