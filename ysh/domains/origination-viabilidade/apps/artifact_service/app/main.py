import json
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, List, Dict, Optional, Union

from fastapi import Body, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, validator


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Handle application startup and shutdown events."""
    load_index()
    yield
    artifact_index.clear()


app = FastAPI(
    title='Artifact Service',
    description='Serviço para armazenamento e recuperação de artefatos para swarms de agentes',
    version='0.1.0',
    lifespan=lifespan,
)

STORAGE_DIR = Path(os.getenv('ARTIFACT_STORAGE_DIR', './data'))
STORAGE_DIR.mkdir(exist_ok=True)

artifact_index: Dict[str, Path] = {}


def load_index():
    """Load existing artifacts from the storage directory."""
    for artifact_type in ['contracts', 'proposals']:
        type_dir = STORAGE_DIR / artifact_type
        type_dir.mkdir(exist_ok=True)
        for file_path in type_dir.glob('*.json'):
            artifact_id = file_path.stem
            artifact_index[artifact_id] = file_path
            
# Modelos comuns
class SwarmContext(BaseModel):
    """Contexto para coordenação de swarms."""
    swarm_id: Optional[str] = None
    trace_id: Optional[str] = None
    parent_swarm_ids: Optional[List[str]] = None


class Artifact(BaseModel):
    """Represents a data artifact in the system."""

    id: str = Field(..., description='The unique identifier of the artifact.')
    type: str = Field(
        ..., description="The type of the artifact (e.g., 'contract')."
    )
    content: dict[str, Any] = Field(..., description="The artifact's content.")


@app.post(
    '/artifacts/{artifact_type}', status_code=201, response_model=Artifact
)
async def create_artifact(
    artifact_type: str,
    content: Annotated[dict[str, Any], Body()],
):
    """Create a new artifact (contract or proposal)."""
    if artifact_type not in ['contracts', 'proposals']:
        raise HTTPException(status_code=400, detail='Invalid artifact type.')

    artifact_id = str(uuid.uuid4())
    content[f'{artifact_type[:-1]}Id'] = artifact_id

    type_dir = STORAGE_DIR / artifact_type
    file_path = type_dir / f'{artifact_id}.json'

    try:
        with file_path.open('w') as f:
            json.dump(content, f, indent=2)
    except OSError as e:
        raise HTTPException(
            status_code=500, detail=f'Failed to write artifact: {e}'
        ) from e

    artifact_index[artifact_id] = file_path
    return {'id': artifact_id, 'type': artifact_type, 'content': content}


@app.get(
    '/artifacts/{artifact_type}/{artifact_id}',
    response_model=Artifact,
)
async def get_artifact(artifact_type: str, artifact_id: str):
    """Retrieve an artifact by its type and ID."""
    if artifact_type not in ['contracts', 'proposals']:
        raise HTTPException(status_code=400, detail='Invalid artifact type.')

    file_path = artifact_index.get(artifact_id)

    expected_path_part = (STORAGE_DIR / artifact_type).name
    if not file_path or expected_path_part not in str(file_path):
        raise HTTPException(status_code=404, detail='Artifact not found.')

    try:
        with file_path.open() as f:
            read_content: dict[str, Any] = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise HTTPException(
            status_code=500, detail=f'Failed to read artifact: {e}'
        ) from e

    return {'id': artifact_id, 'type': artifact_type, 'content': read_content}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8005)
