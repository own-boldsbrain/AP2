from datetime import datetime, timezone

from sqlalchemy import Float, JSON, Boolean, ForeignKey, Numeric, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


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

    geo_kpis: Mapped["LeadGeoKPIs" | None] = relationship(
        back_populates="lead", uselist=False
    )


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


class LeadGeoKPIs(Base):
    __tablename__ = "lead_geo_kpis"

    composite_key: Mapped[str] = mapped_column(String, primary_key=True)
    lead_id: Mapped[str] = mapped_column(
        String, ForeignKey("leads.lead_id"), unique=True, index=True
    )
    cpf: Mapped[str] = mapped_column(String(32))
    cep: Mapped[str] = mapped_column(String(16))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    properties: Mapped[dict] = mapped_column(JSON, default=dict)
    kpis: Mapped[dict] = mapped_column(JSON, default=dict)
    geojson: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    lead: Mapped[Lead] = relationship(back_populates="geo_kpis")
