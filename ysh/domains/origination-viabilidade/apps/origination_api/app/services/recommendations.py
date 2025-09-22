from collections.abc import Iterable
from pathlib import Path
import uuid

import yaml

from app.services.sizing import choose_band, sizing_summary

CONFIG_DIR = Path(__file__).resolve().parents[2] / "configs"


def _load_yaml(name: str) -> dict:
    with (CONFIG_DIR / name).open("r", encoding="utf-8") as fp:
        return yaml.safe_load(fp)


PROJECT_BANDS = _load_yaml("project_size_bands.yaml")["bands"]
TIERS = {tier["code"]: tier for tier in _load_yaml("recommendation_tiers.yaml")["tiers"]}
UPSELL = _load_yaml("upsell_rules.yaml")["rules"]


def _matches(expected: Iterable, value: str | None) -> bool:
    return value is not None and value in expected


def _suggest_from_rules(band_code: str, context: dict) -> list[str]:
    suggestions: set[str] = set()
    for rule in UPSELL:
        when = rule.get("when", {})
        match = True
        for key, expected in when.items():
            if key == "band_in":
                values = expected if isinstance(expected, list) else [expected]
                if not _matches(values, band_code):
                    match = False
                    break
            else:
                ctx_value = context.get(key)
                if isinstance(expected, list):
                    if not _matches(expected, ctx_value):
                        match = False
                        break
                else:
                    if ctx_value != expected:
                        match = False
                        break
        if match:
            suggestions.update(rule.get("suggest", []))
    return sorted(suggestions)


def build_bundle(features: dict, preferred_tier: str | None) -> dict:
    tier_code = preferred_tier or "T115"
    tier = TIERS[tier_code]
    summary = sizing_summary(features, tier["factor"])
    kwp = summary["kwp"]
    band_code, band = choose_band(kwp, PROJECT_BANDS)
    context = {
        "hsp": summary["hsp"],
        "pr": summary["pr"],
        "losses": summary["losses"],
        "load_profile": features.get("load_profile"),
        "generation_modality": features.get("generation_modality"),
        "uc_type": features.get("uc_type"),
    }
    rule_suggestions = _suggest_from_rules(band_code, context)
    combined_upsell = sorted(set(tier["upsell_triggers"]) | set(rule_suggestions))
    offers = [
        {
            "sku": f"{band_code}-BASE",
            "title": f"Kit {band_code} Base",
            "capex_estimate": 1000 * max(kwp, 1),
            "payback_estimate": 48,
            "upsell": combined_upsell,
        },
        {
            "sku": f"{band_code}-PLUS",
            "title": f"Kit {band_code} Plus",
            "capex_estimate": 1100 * max(kwp, 1),
            "payback_estimate": 54,
            "upsell": combined_upsell,
        },
        {
            "sku": f"{band_code}-PRO",
            "title": f"Kit {band_code} Pro",
            "capex_estimate": 1200 * max(kwp, 1),
            "payback_estimate": 60,
            "upsell": combined_upsell,
        },
    ]
    return {
        "id": str(uuid.uuid4()),
        "tier_code": tier_code,
        "band_code": band_code,
        "kwp": kwp,
        "expected_kwh_year": summary["expected_kwh_year"],
        "offers": offers,
        "context": context,
        "upsell": combined_upsell,
        "sizing": summary,
    }
