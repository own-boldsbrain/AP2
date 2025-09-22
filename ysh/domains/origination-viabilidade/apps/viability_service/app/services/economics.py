"""Módulo para cálculos econômicos de sistemas fotovoltaicos."""

from typing import List

from pydantic import BaseModel


class EconomicsIn(BaseModel):
    """
    Dados de entrada para avaliação econômica.

    Attributes:
        kwh_year: Geração anual em kWh
        tariff_profile: Perfil tarifário da distribuidora
        capex: Custo de capital (R$)
        opex: Custo operacional anual (R$)
        lifetime_years: Vida útil do sistema em anos
        degradation_pct_year: Degradação anual em porcentagem
        discount_rate_pct: Taxa de desconto anual em porcentagem
    """
    kwh_year: float
    tariff_profile: dict
    capex: float
    opex: float
    lifetime_years: int = 25
    degradation_pct_year: float = 0.5
    discount_rate_pct: float = 10.0


class EconomicsOut(BaseModel):
    """
    Resultado da avaliação econômica.

    Attributes:
        roi_pct: Retorno sobre investimento em porcentagem
        payback_years: Tempo de retorno em anos
        tir_pct: Taxa interna de retorno em porcentagem
        cashflow: Fluxo de caixa anual
    """
    roi_pct: float
    payback_years: float
    tir_pct: float
    cashflow: List[float]


def evaluate(in_: EconomicsIn) -> EconomicsOut:
    """
    Avalia a viabilidade econômica de um sistema fotovoltaico.

    Args:
        in_: Dados de entrada para avaliação

    Returns:
        Resultado da avaliação econômica
    """
    # Simplificação: receita = kwh_year * tarifa média (R$/kWh)
    tariff_r_per_kwh = (in_.tariff_profile.get("cents_per_kwh") or 100) / 100.0
    cash = []
    kwh = in_.kwh_year

    # Calcula o fluxo de caixa para cada ano
    for y in range(1, in_.lifetime_years + 1):
        rev = kwh * tariff_r_per_kwh
        net = rev - in_.opex
        # No primeiro ano, subtrai o CAPEX
        cash.append(net if y > 1 else net - in_.capex)
        # Aplica degradação anual
        kwh *= (1 - in_.degradation_pct_year / 100.0)

    # Calcula o payback
    cum = 0.0
    payback = float(in_.lifetime_years)
    for i, v in enumerate(cash, start=1):
        cum += v
        if cum >= 0:
            payback = i
            break

    # Calcula o ROI
    roi = (sum(cash) / in_.capex) * 100 if in_.capex > 0 else 0.0

    # TIR simplificada (busca bruta)
    tir = 0.0
    try:
        for r in [x / 100 for x in range(1, 51)]:
            npv = sum(cash[t] / ((1 + r) ** (t + 0)) for t in range(len(cash)))
            if npv >= 0:
                tir = r * 100
                break
    except Exception:
        pass

    return EconomicsOut(
        roi_pct=round(roi, 1),
        payback_years=float(payback),
        tir_pct=round(tir, 1),
        cashflow=[round(x, 2) for x in cash]
    )    )
