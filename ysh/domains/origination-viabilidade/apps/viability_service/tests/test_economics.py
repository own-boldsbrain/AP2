"""Tests for the economic viability helpers."""

from app.services.economics import EconomicsIn, evaluate


def test_evaluate_returns_rounded_metrics() -> None:
    """The economics evaluation should round its numeric outputs."""

    result = evaluate(
        EconomicsIn(
            kwh_year=15_000,
            tariff_profile={"cents_per_kwh": 80},
            capex=10_000,
            opex=500,
            lifetime_years=5,
            degradation_pct_year=0.5,
        )
    )

    assert result.payback_years == 1.0
    assert result.roi_pct == 469.0
    assert result.tir_pct == 1.0
    assert result.cashflow == [
        1500.0,
        11440.0,
        11380.3,
        11320.9,
        11261.79,
    ]
