from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import SessionLocal
from app.events.nats_bus import SUBJECTS, publish
from app.models.leads import Lead, LeadFeatures, LeadGeoKPIs, Recommendation
from app.schemas.leads import (
    ClassifyIn,
    GeoKPIIn,
    GeoKPIOut,
    LeadCreate,
    LeadOut,
    ModalityIn,
    RecommendationOut,
    SizingIn,
    SizingOut,
)
from app.services.geo_enrichment import build_geo_key, build_geojson_feature
from app.services.recommendations import PROJECT_BANDS, TIERS, build_bundle
from app.services.sizing import choose_band, sizing_summary

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
    "/leads/{lead_id}/geo-kpis",
    response_model=GeoKPIOut,
    summary="Registrar dados GeoJSON enriquecidos com KPIs regulatórios",
)
async def upsert_geo_kpis(
    lead_id: str,
    body: GeoKPIIn,
    db: AsyncSession = Depends(get_db),
):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "lead not found")

    composite_key = build_geo_key(body.cpf, body.cep, body.latitude, body.longitude)
    feature = build_geojson_feature(
        cpf=body.cpf,
        cep=body.cep,
        latitude=body.latitude,
        longitude=body.longitude,
        kpis=body.kpis.model_dump(),
        properties=body.properties,
    )

    existing = await db.get(LeadGeoKPIs, composite_key)
    if existing and existing.lead_id != lead_id:
        raise HTTPException(409, "geo KPIs belong to another lead")
    if existing:
        target = existing
    else:
        target = LeadGeoKPIs(composite_key=composite_key, lead_id=lead_id)
        db.add(target)

    props = feature["properties"]
    target.lead_id = lead_id
    target.cpf = props.get("cpf", "")
    target.cep = props.get("cep", "")
    target.latitude = feature["geometry"]["coordinates"][1]
    target.longitude = feature["geometry"]["coordinates"][0]
    target.properties = props
    target.kpis = props.get("kpis", {})
    target.geojson = feature

    await db.commit()
    await db.refresh(target)
    return GeoKPIOut.model_validate(target)


@router.get(
    "/leads/{lead_id}/geo-kpis",
    response_model=GeoKPIOut,
    summary="Consultar KPIs geoespaciais do lead",
)
async def get_geo_kpis(lead_id: str, db: AsyncSession = Depends(get_db)):
    record = (
        await db.execute(
            select(LeadGeoKPIs).where(LeadGeoKPIs.lead_id == lead_id)
        )
    ).scalar_one_or_none()
    if not record:
        raise HTTPException(404, "geo KPIs not found")
    return GeoKPIOut.model_validate(record)


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
    band_code, _ = choose_band(summary["kwp"], PROJECT_BANDS)
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
        "band_code": band_code,
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
