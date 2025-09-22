import pytest

from app.services.recommendations import build_bundle
from app.services.sizing import sizing_summary


def test_sizing_summary_basic() -> None:
    summary = sizing_summary({"consumo_12m_kwh": 6000, "hsp": 5.0}, tier_factor=1.15)
    assert summary["kwp"] == pytest.approx(5.5)
    assert summary["expected_kwh_year"] == pytest.approx(6906)
    assert summary["pr"] == pytest.approx(0.80)
    assert summary["losses"] == pytest.approx(0.14)


def test_build_bundle_upsell_rules_applied() -> None:
    bundle = build_bundle(
        {
            "consumo_12m_kwh": 6000,
            "hsp": 5.0,
            "load_profile": "R-N",
            "generation_modality": "COMPARTILHADA",
            "uc_type": "COND_MUC",
        },
        preferred_tier="T115",
    )
    assert bundle["band_code"] == "S"
    # Tier triggers + rule suggestions merged without duplicates
    assert "BATERIA_LIGHT" in bundle["upsell"]
    assert "RATEIO_AUTOMATION" in bundle["upsell"]
    assert "RATEIO_MUC" in bundle["upsell"]
    # Offers inherit combined upsell list
    for offer in bundle["offers"]:
        assert set(bundle["upsell"]).issuperset(set(offer["upsell"]))
