from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


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
