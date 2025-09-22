"""FastAPI application that exposes the MMGD providers dataset."""

from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query

from .data import DATASET, PROVIDERS_BY_ID
from .schemas import DatasetMetadata, GlobalInfo, Provider, SubmissionInfo


def _filter_by_state(providers: List[Provider], state: str) -> List[Provider]:
    state_upper = state.upper()
    return [
        provider
        for provider in providers
        if any(candidate.upper() == state_upper for candidate in provider.states)
    ]


def _filter_by_group(providers: List[Provider], group: str) -> List[Provider]:
    group_lower = group.lower()
    return [
        provider for provider in providers if provider.group.lower() == group_lower
    ]


def _filter_by_submission_type(
    providers: List[Provider], submission_type: str
) -> List[Provider]:
    submission_type_lower = submission_type.lower()
    return [
        provider
        for provider in providers
        if provider.submission.type.lower() == submission_type_lower
    ]


app = FastAPI(
    title="MMGD Providers API",
    version=DATASET.version,
    description=(
        "Catálogo em FastAPI dos portais públicos de homologação MMGD por"
        " distribuidora, conforme bootstrap fornecido."
    ),
)


@app.get("/metadata", response_model=DatasetMetadata, tags=["dataset"])
def get_metadata() -> DatasetMetadata:
    """Return API metadata and simple statistics."""

    return DatasetMetadata(
        api=DATASET.api,
        version=DATASET.version,
        updated_at=DATASET.updated_at,
        provider_count=len(DATASET.providers),
    )


@app.get("/global", response_model=GlobalInfo, tags=["dataset"])
def get_global_info() -> GlobalInfo:
    """Return dataset-wide ANEEL references and legal norms."""

    return DATASET.global_


@app.get("/providers", response_model=List[Provider], tags=["providers"])
def list_providers(
    state: Optional[str] = Query(
        default=None,
        description="Filter providers by federative unit (sigla do estado).",
        min_length=2,
        max_length=2,
    ),
    group: Optional[str] = Query(
        default=None, description="Filter providers by holding/group name."
    ),
    submission_type: Optional[str] = Query(
        default=None,
        description="Filter by submission.type (ex.: web_portal, web_portal_docs).",
    ),
) -> List[Provider]:
    """Return the list of providers, optionally filtered by query parameters."""

    providers: List[Provider] = list(DATASET.providers)

    if state:
        providers = _filter_by_state(providers, state)
    if group:
        providers = _filter_by_group(providers, group)
    if submission_type:
        providers = _filter_by_submission_type(providers, submission_type)

    return providers


@app.get("/providers/{provider_id}", response_model=Provider, tags=["providers"])
def get_provider(provider_id: str) -> Provider:
    """Return a single provider by its identifier."""

    provider = PROVIDERS_BY_ID.get(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@app.get(
    "/providers/{provider_id}/submission",
    response_model=SubmissionInfo,
    tags=["providers"],
)
def get_provider_submission(provider_id: str) -> SubmissionInfo:
    """Return only the submission block for a provider."""

    provider = PROVIDERS_BY_ID.get(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider.submission
