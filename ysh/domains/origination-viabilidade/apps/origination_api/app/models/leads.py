from sqlalchemy import JSON, Boolean, Numeric, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Lead(Base):
    __tablename__ = "leads"

    lead_id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    source: Mapped[str | None] = mapped_column(String(120))
    name: Mapped[str | None] = mapped_column(String(160))
    email: Mapped[str | None] = mapped_column(String(160))
    phone: Mapped[str | None] = mapped_column(String(40))
    cpf_cnpj: Mapped[str | None] = mapped_column(String(80))
    cep: Mapped[str | None] = mapped_column(String(12))
    uf: Mapped[str | None] = mapped_column(String(2))
    municipio: Mapped[str | None] = mapped_column(String(120))
    consent: Mapped[bool] = mapped_column(Boolean, default=False)

    tariff_group: Mapped[str | None] = mapped_column(String(8))
    consumer_class: Mapped[str | None] = mapped_column(String(16))
    consumer_subclass: Mapped[str | None] = mapped_column(String(24))
    uc_type: Mapped[str | None] = mapped_column(String(32))
    generation_modality: Mapped[str | None] = mapped_column(String(20))
    ug_type: Mapped[str | None] = mapped_column(String(24))

    tier: Mapped[str | None] = mapped_column(String(8))
    region: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str | None] = mapped_column(String(32))


class LeadFeatures(Base):
    __tablename__ = "lead_features"

    lead_id: Mapped[str] = mapped_column(String, primary_key=True)
    score_engagement: Mapped[float | None] = mapped_column(Numeric)
    score_finance: Mapped[float | None] = mapped_column(Numeric)
    hsp: Mapped[float | None] = mapped_column(Numeric)
    consumo_12m_kwh: Mapped[float | None] = mapped_column(Numeric)
    load_profile: Mapped[str | None] = mapped_column(String(16))
    load_factor: Mapped[float | None] = mapped_column(Numeric)
    tou_sensitivity: Mapped[dict | None] = mapped_column(JSON)
    seasonal_index: Mapped[dict | None] = mapped_column(JSON)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    lead_id: Mapped[str] = mapped_column(String, index=True)
    tier_code: Mapped[str | None] = mapped_column(String(8))
    band_code: Mapped[str | None] = mapped_column(String(8))
    kwp: Mapped[float | None] = mapped_column(Numeric)
    expected_kwh_year: Mapped[float | None] = mapped_column(Numeric)
    upsell: Mapped[dict | None] = mapped_column(JSON)
    details: Mapped[dict | None] = mapped_column(JSON)
