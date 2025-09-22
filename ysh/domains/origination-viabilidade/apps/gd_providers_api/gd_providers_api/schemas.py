"""Pydantic models describing the MMGD providers dataset."""

from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

try:  # pragma: no cover - compatibility shim for Pydantic v1.
    from pydantic import ConfigDict
except ImportError:  # pragma: no cover
    ConfigDict = None  # type: ignore[misc]


class SubmissionRequirements(BaseModel):
    """Authentication and anti-bot requirements for a provider portal."""

    login_required: Optional[Union[bool, str]] = Field(
        default=None,
        description=(
            "Indicates whether authentication is required. Some providers"
            " report special cases as strings."
        ),
    )
    captcha: Optional[Union[bool, str]] = Field(
        default=None, description="Whether a CAPTCHA challenge is present."
    )
    captcha_vendor_hint: Optional[str] = Field(
        default=None, description="Optional hint about the CAPTCHA technology."
    )


class SubmissionInfo(BaseModel):
    """Information about how to submit distributed generation requests."""

    type: str
    urls: Dict[str, str]
    requirements: SubmissionRequirements
    notes: Optional[str] = None


class DocsInfo(BaseModel):
    """Additional documentation links."""

    howto: Optional[List[str]] = None


class Provider(BaseModel):
    """Represents a distribution utility that accepts MMGD requests."""

    id: str
    name: str
    group: str
    states: List[str]
    submission: SubmissionInfo
    docs: Optional[DocsInfo] = None
    notes: Optional[str] = None


class GlobalInfo(BaseModel):
    """Dataset-wide references applicable to all providers."""

    aneel_forms_page: str
    legal_refs: List[str]


class ProvidersDataset(BaseModel):
    """Full dataset published by the user."""

    api: str
    version: str
    updated_at: date
    global_: GlobalInfo = Field(alias="global")
    providers: List[Provider]

    if ConfigDict is not None:  # pragma: no branch
        model_config = ConfigDict(populate_by_name=True)
    else:  # pragma: no cover
        class Config:  # type: ignore[no-redef]
            allow_population_by_field_name = True


class DatasetMetadata(BaseModel):
    """Summary statistics about the dataset."""

    api: str
    version: str
    updated_at: date
    provider_count: int
