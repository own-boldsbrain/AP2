from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class LeadCreate(BaseModel):
    lead_id: str
    source: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    consent: bool = Field(default=False)
    cep: Optional[str] = None
    uf: Optional[str] = None
    municipio: Optional[str] = None
    tariff_group: Optional[str] = None
    consumer_class: Optional[str] = None
    consumer_subclass: Optional[str] = None
    uc_type: Optional[str] = None
    generation_modality: Optional[str] = None
    ug_type: Optional[str] = None


class LeadOut(BaseModel):
    lead_id: str
    status: Optional[str] = None


class ClassifyIn(BaseModel):
    tariff_group: Optional[str] = None
    consumer_class: Optional[str] = None
    consumer_subclass: Optional[str] = None
    uc_type: Optional[str] = None


class ModalityIn(BaseModel):
    generation_modality: str
    principal_uc: Optional[str] = None
    members: Optional[List[dict]] = None


class SizingIn(BaseModel):
    preferred_tier: Optional[str] = None  # T115/T130/T145/T160


class SizingOut(BaseModel):
    lead_id: str
    band_code: str
    kwp: float
    expected_kwh_year: float
    pr: float
    losses: float


class RecommendationOut(BaseModel):
    tier_code: str
    band_code: str
    kwp: float
    expected_kwh_year: float
    offers: list
    upsell: List[str] = Field(default_factory=list)


class KPIBundle(BaseModel):
    bacen: Dict[str, Any] = Field(default_factory=dict)
    epe: Dict[str, Any] = Field(default_factory=dict)
    aneel: Dict[str, Any] = Field(default_factory=dict)
    ibge: Dict[str, Any] = Field(default_factory=dict)
    quod: Dict[str, Any] = Field(default_factory=dict)


class GeoKPIIn(BaseModel):
    cpf: str
    cep: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    kpis: KPIBundle = Field(default_factory=KPIBundle)
    properties: Dict[str, Any] = Field(default_factory=dict)


class GeoKPIOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lead_id: str
    composite_key: str
    cpf: str
    cep: str
    latitude: float
    longitude: float
    properties: Dict[str, Any]
    geojson: Dict[str, Any]
    kpis: KPIBundle
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator("kpis", mode="before")
    @classmethod
    def _ensure_bundle(cls, value: Dict[str, Any] | KPIBundle) -> KPIBundle:
        if isinstance(value, KPIBundle):
            return value
        return KPIBundle(**value)
