"""Deterministic economic evaluation helpers used by the viability service."""

from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field


class EconomicsIn(BaseModel):
    """Input contract for ``/tools/economics.evaluate``."""

    kwh_year: float = Field(gt=0)
    tariff_profile: Dict[str, float] = Field(default_factory=dict)
    capex: float = Field(gt=0)
    opex: float = Field(ge=0)
    lifetime_years: int = Field(default=25, ge=1)
    degradation_pct_year: float = Field(default=0.5, ge=0, lt=100)
    discount_rate_pct: float = Field(default=10.0, ge=0)


class EconomicsOut(BaseModel):
    roi_pct: float
    payback_years: float
    tir_pct: float
    cashflow: List[float]


def evaluate(inp: EconomicsIn) -> EconomicsOut:
    """Compute ROI, payback and IRR using a simplified cashflow model."""

    tariff_r_per_kwh = (inp.tariff_profile.get("cents_per_kwh") or 100.0) / 100.0
    energy = inp.kwh_year
    cashflow: List[float] = []

    for year in range(1, inp.lifetime_years + 1):
        revenue = energy * tariff_r_per_kwh
        net = revenue - inp.opex
        if year == 1:
            net -= inp.capex
        cashflow.append(round(net, 2))
        # apply yearly degradation
        energy *= 1 - inp.degradation_pct_year / 100.0

    cumulative = 0.0
    payback_years = float(inp.lifetime_years)
    for idx, value in enumerate(cashflow, start=1):
        cumulative += value
        if cumulative >= 0:
            payback_years = float(idx)
            break

    roi_pct = round((sum(cashflow) / inp.capex) * 100.0, 1)
    tir_pct = _compute_irr(cashflow, inp.discount_rate_pct)

    return EconomicsOut(
        roi_pct=roi_pct,
        payback_years=payback_years,
        tir_pct=tir_pct,
        cashflow=cashflow,
    )


def _compute_irr(cashflow: List[float], fallback_rate_pct: float) -> float:
    """Approximate the internal rate of return.

    The function performs a bounded linear search which is deterministic and
    dependency-free, making it ideal for unit tests.  If the cashflow never
    becomes positive the provided ``fallback_rate_pct`` is returned.
    """

    target = fallback_rate_pct / 100.0
    if not cashflow:
        return round(target * 100, 1)

    def npv(rate: float) -> float:
        return sum(value / ((1 + rate) ** idx) for idx, value in enumerate(cashflow, start=1))

    rate = 0.0
    step = 0.001
    max_rate = 0.5
    while rate <= max_rate:
        if npv(rate) >= 0:
            return round(rate * 100, 1)
        rate += step

    return round(target * 100, 1)
