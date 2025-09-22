from typing import Any, Dict, Tuple

from typing import Any, Dict, Tuple

DEFAULT_PR = 0.80
DEFAULT_LOSSES = 0.14
DAYS = 365


def _normalize_hsp(hsp: float | None) -> float:
    """Avoid division by zero by ensuring a minimum HSP."""

    return max(float(hsp or 0.0), 0.1)


def compute_kwp(
    consumo_anual_kwh: float,
    hsp: float,
    tier_factor: float,
    pr: float = DEFAULT_PR,
    losses: float = DEFAULT_LOSSES,
) -> float:
    denom = _normalize_hsp(hsp) * DAYS * pr * (1 - losses)
    return round((consumo_anual_kwh * tier_factor) / denom, 2)


def expected_kwh_year(
    kwp: float,
    hsp: float,
    pr: float = DEFAULT_PR,
    losses: float = DEFAULT_LOSSES,
) -> float:
    return round(kwp * _normalize_hsp(hsp) * DAYS * pr * (1 - losses), 0)


def sizing_summary(
    features: Dict[str, Any],
    tier_factor: float,
    pr: float = DEFAULT_PR,
    losses: float = DEFAULT_LOSSES,
) -> Dict[str, float]:
    consumo = float(features.get("consumo_12m_kwh") or 0.0)
    hsp = float(features.get("hsp") or 0.0)
    kwp = compute_kwp(consumo, hsp, tier_factor, pr=pr, losses=losses)
    return {
        "kwp": kwp,
        "expected_kwh_year": expected_kwh_year(kwp, hsp, pr=pr, losses=losses),
        "pr": pr,
        "losses": losses,
        "hsp": round(_normalize_hsp(hsp), 2),
    }


def choose_band(kwp: float, bands: list[dict]) -> Tuple[str, dict]:
    for band in bands:
        lo, hi = band["kwp_range"]
        if kwp >= lo and kwp < hi:
            return band["code"], band
    return bands[-1]["code"], bands[-1]
