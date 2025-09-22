from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionLocal
from app.events.nats_bus import SUBJECTS, publish
from app.models.leads import Lead, LeadFeatures, Recommendation
from app.schemas.leads import (
    ClassifyIn,
    LeadCreate,
    LeadOut,
    ModalityIn,
    RecommendationOut,
    SizingIn,
    SizingOut,
)
from app.services.recommendations import TIERS, build_bundle
from app.services.sizing import sizing_summary

router = APIRouter()


async def get_db():
    async with SessionLocal() as session:
        yield session


@router.post(
    "/leads",
    response_model=LeadOut,
    summary="Capturar lead",
    status_code=status.HTTP_201_CREATED,
)
async def create_lead(body: LeadCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.get(Lead, body.lead_id)
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "lead already exists")
    lead = Lead(**body.model_dump())
    db.add(lead)
    await db.commit()
    await publish(
        SUBJECTS["lead_captured"],
        {
            "lead_id": body.lead_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            "source": body.source or "unknown",
            "consent": body.consent,
        },
    )
    return {"lead_id": body.lead_id, "status": "created"}


@router.post("/leads/{lead_id}/classify", summary="Classificar classe/UC & detectar perfil")
async def classify_lead(
    lead_id: str, body: ClassifyIn, db: AsyncSession = Depends(get_db)
):
    lead = (
        await db.execute(select(Lead).where(Lead.lead_id == lead_id))
    ).scalar_one_or_none()
    if not lead:
        raise HTTPException(404, "lead not found")
    for key, value in body.model_dump(exclude_none=True).items():
        setattr(lead, key, value)
    features = (
        await db.execute(select(LeadFeatures).where(LeadFeatures.lead_id == lead_id))
    ).scalar_one_or_none()
    if not features:
        features = LeadFeatures(
            lead_id=lead_id,
            hsp=5.0,
            consumo_12m_kwh=6000,
            load_profile="C-D",
            load_factor=0.6,
        )
        db.add(features)
    await db.commit()
    await publish(
        SUBJECTS["profile_detected"],
        {
            "lead_id": lead_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            "consumer_class": lead.consumer_class or "UNKNOWN",
            "uc_type": lead.uc_type or "UNKNOWN",
            "load_profile": features.load_profile or "UNKNOWN",
            "features": {
                "load_factor": float(features.load_factor or 0.6),
                "hsp": float(features.hsp or 5.0),
            },
        },
    )
    return {"ok": True}


@router.post(
    "/leads/{lead_id}/modality",
    summary="Selecionar modalidade SCEE (AUTO_LOCAL/REMOTO/GC/MUC)",
    status_code=status.HTTP_201_CREATED,
)
async def set_modality(
    lead_id: str, body: ModalityIn, db: AsyncSession = Depends(get_db)
):
    lead = (
        await db.execute(select(Lead).where(Lead.lead_id == lead_id))
    ).scalar_one_or_none()
    if not lead:
        raise HTTPException(404, "lead not found")
    lead.generation_modality = body.generation_modality
    await db.commit()
    await publish(
        SUBJECTS["modality_selected"],
        {
            "lead_id": lead_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            "generation_modality": body.generation_modality,
            "allocation": {
                "principal_uc": body.principal_uc,
                "members": body.members or [],
            },
        },
    )
    return {"ok": True}


@router.post(
    "/leads/{lead_id}/size",
    response_model=SizingOut,
    summary="Calcular dimensionamento (kWp)",
)
async def size_lead(
    lead_id: str,
    body: SizingIn | None = None,
    db: AsyncSession = Depends(get_db),
):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "lead not found")
    features = (
        await db.execute(select(LeadFeatures).where(LeadFeatures.lead_id == lead_id))
    ).scalar_one_or_none()
    if not features:
        raise HTTPException(400, "features missing")
    tier_code = (body and body.preferred_tier) or lead.tier or "T115"
    tier = TIERS.get(tier_code)
    if not tier:
        raise HTTPException(400, "invalid tier")
    feature_payload = {
        "consumo_12m_kwh": float(features.consumo_12m_kwh or 0.0),
        "hsp": float(features.hsp or 0.0),
        "generation_modality": lead.generation_modality,
        "uc_type": lead.uc_type,
        "load_profile": features.load_profile,
    }
    summary = sizing_summary(feature_payload, tier["factor"])
    now = datetime.now(timezone.utc).isoformat()
    await publish(
        SUBJECTS["sized"],
        {
            "lead_id": lead_id,
            "ts": now,
            "kwp": summary["kwp"],
            "kwh_year": summary["expected_kwh_year"],
            "pr": summary["pr"],
            "losses": summary["losses"],
        },
    )
    return {
        "lead_id": lead_id,
        "kwp": summary["kwp"],
        "expected_kwh_year": summary["expected_kwh_year"],
        "pr": summary["pr"],
        "losses": summary["losses"],
    }


@router.post(
    "/leads/{lead_id}/recommendations",
    response_model=RecommendationOut,
    summary="Gerar recomendações",
    status_code=status.HTTP_201_CREATED,
)
async def recommendations(
    lead_id: str, body: SizingIn, db: AsyncSession = Depends(get_db)
):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "lead not found")
    features = (
        await db.execute(select(LeadFeatures).where(LeadFeatures.lead_id == lead_id))
    ).scalar_one_or_none()
    if not features:
        raise HTTPException(400, "features missing")
    bundle = build_bundle(
        {
            "consumo_12m_kwh": float(features.consumo_12m_kwh or 6000),
            "hsp": float(features.hsp or 5.0),
            "load_profile": features.load_profile,
            "generation_modality": lead.generation_modality,
            "uc_type": lead.uc_type,
        },
        body.preferred_tier or lead.tier,
    )
    recommendation = Recommendation(
        id=bundle["id"],
        lead_id=lead_id,
        tier_code=bundle["tier_code"],
        band_code=bundle["band_code"],
        kwp=bundle["kwp"],
        expected_kwh_year=bundle["expected_kwh_year"],
        upsell={"suggested": bundle["upsell"]},
        details={**bundle["context"], "tier_factor": TIERS[bundle["tier_code"]]["factor"]},
    )
    db.add(recommendation)
    await db.commit()
    now = datetime.now(timezone.utc).isoformat()
    await publish(
        SUBJECTS["sized"],
        {
            "lead_id": lead_id,
            "ts": now,
            "kwp": bundle["kwp"],
            "kwh_year": bundle["expected_kwh_year"],
            "pr": bundle["sizing"]["pr"],
            "losses": bundle["sizing"]["losses"],
        },
    )
    await publish(
        SUBJECTS["reco_bundle"],
        {
            "lead_id": lead_id,
            "ts": now,
            **bundle,
        },
    )
    return {
        "tier_code": bundle["tier_code"],
        "band_code": bundle["band_code"],
        "kwp": bundle["kwp"],
        "expected_kwh_year": bundle["expected_kwh_year"],
        "offers": bundle["offers"],
        "upsell": bundle["upsell"],
    }
