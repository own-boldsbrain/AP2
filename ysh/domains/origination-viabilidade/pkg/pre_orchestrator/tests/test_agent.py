"""
Testes unitários para o agente orquestrador PRE.
"""

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pkg.pre_orchestrator.agent import PREOrchestratorAgent


@pytest.fixture
def mock_http_client():
    """Fixture para simular o cliente HTTP."""
    mock = MagicMock()
    mock.get = AsyncMock()
    mock.post = AsyncMock()
    mock.put = AsyncMock()
    return mock


@pytest.fixture
def mock_nats_client():
    """Fixture para simular o cliente NATS."""
    mock = MagicMock()
    mock.publish = AsyncMock()
    return mock


@pytest.fixture
def agent(mock_http_client, mock_nats_client):
    """Fixture para o agente orquestrador PRE."""
    agent = PREOrchestratorAgent(
        http_client=mock_http_client,
        nats_client=mock_nats_client,
        tariff_service_url="http://mock-tariff-service",
        viability_service_url="http://mock-viability-service",
        proposal_service_url="http://mock-proposal-service",
        lead_service_url="http://mock-lead-service",
    )
    return agent


@pytest.mark.asyncio
async def test_create_and_validate_lead(agent, mock_http_client):
    """Testa a criação e validação de lead."""
    # Arrange
    lead_data = {
        "name": "João Silva",
        "email": "joao.silva@exemplo.com",
        "phone": "21999999999",
        "consent": True,
        "cep": "22000-000",
        "uf": "RJ",
        "municipio": "Rio de Janeiro",
    }

    mock_http_client.post.return_value = AsyncMock(
        status=200,
        json=AsyncMock(
            return_value={
                "lead_id": str(uuid.uuid4()),
                "status": "valid",
                "name": lead_data["name"],
                "email": lead_data["email"],
                "phone": lead_data["phone"],
                "consent": lead_data["consent"],
                "cep": lead_data["cep"],
                "uf": lead_data["uf"],
                "municipio": lead_data["municipio"],
                "lat": -22.9,
                "lon": -43.2,
            }
        ),
    )

    # Act
    result = await agent.create_and_validate_lead(lead_data)

    # Assert
    assert mock_http_client.post.called
    assert "lead_id" in result
    assert result["status"] == "valid"
    assert result["lat"] is not None
    assert result["lon"] is not None


@pytest.mark.asyncio
async def test_classify_lead(agent, mock_http_client):
    """Testa a classificação de lead."""
    # Arrange
    lead_id = str(uuid.uuid4())
    consumption_data = {
        "consumo_12m_kwh": 4000,
        "fatura_media": 800,
    }

    mock_http_client.post.return_value = AsyncMock(
        status=200,
        json=AsyncMock(
            return_value={
                "lead_id": lead_id,
                "tariff_group": "B1",
                "consumer_class": "RESIDENCIAL",
                "consumer_subclass": "",
                "uc_type": "RESIDENCIAL",
            }
        ),
    )

    # Act
    result = await agent.classify_lead(lead_id, consumption_data)

    # Assert
    assert mock_http_client.post.called
    assert result["tariff_group"] == "B1"
    assert result["consumer_class"] == "RESIDENCIAL"
    assert result["uc_type"] == "RESIDENCIAL"


@pytest.mark.asyncio
async def test_select_generation_modality(agent):
    """Testa a seleção de modalidade de geração."""
    # Arrange
    lead_id = str(uuid.uuid4())
    classification = {
        "tariff_group": "B1",
        "consumer_class": "RESIDENCIAL",
        "uc_type": "RESIDENCIAL",
    }
    preferences = {
        "has_roof": True,
        "multiple_ucs": False,
    }

    # Act
    result = await agent.select_generation_modality(lead_id, classification, preferences)

    # Assert
    assert result["generation_modality"] == "AUTO_LOCAL"
    assert "principal_uc" in result
    assert isinstance(result["members"], list)


@pytest.mark.asyncio
async def test_perform_viability_analysis(agent, mock_http_client):
    """Testa a análise de viabilidade."""
    # Arrange
    lead_id = str(uuid.uuid4())
    location_data = {
        "lat": -22.9,
        "lon": -43.2,
    }
    preferences = {
        "tilt_deg": 20,
        "azimuth_deg": 180,
    }

    mock_http_client.post.return_value = AsyncMock(
        status=200,
        json=AsyncMock(
            return_value={
                "viability_id": str(uuid.uuid4()),
                "lead_id": lead_id,
                "lat": location_data["lat"],
                "lon": location_data["lon"],
                "tilt_deg": preferences["tilt_deg"],
                "azimuth_deg": preferences["azimuth_deg"],
                "mount_type": "fixed",
                "system_loss_fraction": 0.14,
                "hsp": 5.0,
                "pr": 0.80,
                "meteo_source": "NASA_POWER",
                "status": "viable",
            }
        ),
    )

    # Act
    result = await agent.perform_viability_analysis(lead_id, location_data, preferences)

    # Assert
    assert mock_http_client.post.called
    assert "viability_id" in result
    assert result["hsp"] == 5.0
    assert result["pr"] == 0.80
    assert result["status"] == "viable"


@pytest.mark.asyncio
async def test_evaluate_economics(agent, mock_http_client):
    """Testa a avaliação econômica."""
    # Arrange
    lead_id = str(uuid.uuid4())
    system_size_kwp = 7.45
    viability_data = {
        "hsp": 5.0,
        "pr": 0.80,
    }
    classification = {
        "tariff_group": "B1",
        "consumer_class": "RESIDENCIAL",
    }

    expected_kwh_year = system_size_kwp * viability_data["hsp"] * 365 * viability_data["pr"]

    mock_http_client.post.return_value = AsyncMock(
        status=200,
        json=AsyncMock(
            return_value={
                "economics_id": str(uuid.uuid4()),
                "lead_id": lead_id,
                "kwp": system_size_kwp,
                "kwh_year": expected_kwh_year,
                "tariff_profile": {
                    "cents_per_kwh": 120,
                    "connection_type": "monofasico",
                },
                "capex": 52000,
                "opex": 800,
                "roi": 0.18,
                "payback_months": 48,
                "tir": 0.25,
            }
        ),
    )

    # Act
    result = await agent.evaluate_economics(
        lead_id, system_size_kwp, expected_kwh_year, classification
    )

    # Assert
    assert mock_http_client.post.called
    assert "economics_id" in result
    assert "roi" in result
    assert "payback_months" in result
    assert "tir" in result


@pytest.mark.asyncio
async def test_size_system(agent):
    """Testa o dimensionamento do sistema."""
    # Arrange
    lead_id = str(uuid.uuid4())
    consumo_anual = 4000
    viability_data = {
        "hsp": 5.0,
        "pr": 0.80,
        "system_loss_fraction": 0.14,
    }

    # Act
    result = await agent.size_system(lead_id, consumo_anual, viability_data)

    # Assert
    assert "base" in result
    assert "plus" in result
    assert "pro" in result
    assert result["base"]["kwp"] < result["plus"]["kwp"] < result["pro"]["kwp"]
    assert result["base"]["expected_kwh_year"] < result["plus"]["expected_kwh_year"] < result["pro"]["expected_kwh_year"]
    assert "T100" in result["base"]["tier_code"]
    assert "T130" in result["plus"]["tier_code"]
    assert "T160" in result["pro"]["tier_code"]


@pytest.mark.asyncio
async def test_generate_recommendations(agent, mock_http_client):
    """Testa a geração de recomendações."""
    # Arrange
    lead_id = str(uuid.uuid4())
    sizing_results = {
        "base": {
            "kwp": 5.0,
            "expected_kwh_year": 7000,
            "tier_code": "T100",
        },
        "plus": {
            "kwp": 6.5,
            "expected_kwh_year": 9100,
            "tier_code": "T130",
        },
        "pro": {
            "kwp": 8.0,
            "expected_kwh_year": 11200,
            "tier_code": "T160",
        },
    }
    economics_results = {
        "base": {
            "roi": 0.15,
            "payback_months": 60,
            "tir": 0.22,
        },
        "plus": {
            "roi": 0.18,
            "payback_months": 48,
            "tir": 0.25,
        },
        "pro": {
            "roi": 0.20,
            "payback_months": 42,
            "tir": 0.28,
        },
    }

    mock_http_client.post.return_value = AsyncMock(
        status=200,
        json=AsyncMock(
            return_value={
                "recommendation_id": str(uuid.uuid4()),
                "lead_id": lead_id,
                "recommendations": [
                    {
                        "tier": "base",
                        "tier_code": "T100",
                        "band_code": "S",
                        "kwp": 5.0,
                        "expected_kwh_year": 7000,
                        "economics": economics_results["base"],
                    },
                    {
                        "tier": "plus",
                        "tier_code": "T130",
                        "band_code": "M",
                        "kwp": 6.5,
                        "expected_kwh_year": 9100,
                        "economics": economics_results["plus"],
                    },
                    {
                        "tier": "pro",
                        "tier_code": "T160",
                        "band_code": "L",
                        "kwp": 8.0,
                        "expected_kwh_year": 11200,
                        "economics": economics_results["pro"],
                    },
                ],
                "preferred_tier": "plus",
            }
        ),
    )

    # Act
    result = await agent.generate_recommendations(lead_id, sizing_results, economics_results)

    # Assert
    assert mock_http_client.post.called
    assert "recommendation_id" in result
    assert "recommendations" in result
    assert len(result["recommendations"]) == 3
    assert "preferred_tier" in result


@pytest.mark.asyncio
async def test_emit_event(agent, mock_nats_client):
    """Testa a emissão de eventos."""
    # Arrange
    event_type = "lead.captured.v1"
    payload = {
        "lead_id": str(uuid.uuid4()),
        "source": "landing",
        "consent": True,
    }

    # Act
    result = await agent.emit_event(event_type, payload)

    # Assert
    assert mock_nats_client.publish.called
    mock_nats_client.publish.assert_called_once_with(
        f"ysh.events.{event_type}",
        json.dumps(payload).encode()
    )
    assert result["status"] == "emitted"
    assert result["event_type"] == event_type


@pytest.mark.asyncio
async def test_orchestrate_pre_process(agent):
    """Testa a orquestração completa do processo PRE."""
    # Arrange
    with patch.object(agent, 'create_and_validate_lead', new_callable=AsyncMock) as mock_create_lead, \
         patch.object(agent, 'classify_lead', new_callable=AsyncMock) as mock_classify, \
         patch.object(agent, 'select_generation_modality', new_callable=AsyncMock) as mock_select_modality, \
         patch.object(agent, 'perform_viability_analysis', new_callable=AsyncMock) as mock_viability, \
         patch.object(agent, 'size_system', new_callable=AsyncMock) as mock_size, \
         patch.object(agent, 'evaluate_economics', new_callable=AsyncMock) as mock_economics, \
         patch.object(agent, 'generate_recommendations', new_callable=AsyncMock) as mock_recommendations, \
         patch.object(agent, 'emit_event', new_callable=AsyncMock) as mock_emit:

        lead_id = str(uuid.uuid4())
        lead_data = {
            "name": "João Silva",
            "email": "joao.silva@exemplo.com",
            "phone": "21999999999",
            "consent": True,
            "cep": "22000-000",
            "uf": "RJ",
            "municipio": "Rio de Janeiro",
        }
        consumption_data = {
            "consumo_12m_kwh": 4000,
            "fatura_media": 800,
        }
        preferences = {
            "has_roof": True,
            "multiple_ucs": False,
            "tilt_deg": 20,
            "azimuth_deg": 180,
        }

        # Mock de respostas
        validated_lead = {
            "lead_id": lead_id,
            "name": lead_data["name"],
            "email": lead_data["email"],
            "phone": lead_data["phone"],
            "consent": lead_data["consent"],
            "lat": -22.9,
            "lon": -43.2,
        }
        mock_create_lead.return_value = validated_lead

        classification = {
            "tariff_group": "B1",
            "consumer_class": "RESIDENCIAL",
            "uc_type": "RESIDENCIAL",
        }
        mock_classify.return_value = classification

        modality = {
            "generation_modality": "AUTO_LOCAL",
            "principal_uc": "UC123456",
            "members": [],
        }
        mock_select_modality.return_value = modality

        viability = {
            "viability_id": str(uuid.uuid4()),
            "hsp": 5.0,
            "pr": 0.80,
            "system_loss_fraction": 0.14,
            "status": "viable",
        }
        mock_viability.return_value = viability

        sizing_results = {
            "base": {
                "kwp": 5.0,
                "expected_kwh_year": 7000,
                "tier_code": "T100",
            },
            "plus": {
                "kwp": 6.5,
                "expected_kwh_year": 9100,
                "tier_code": "T130",
            },
            "pro": {
                "kwp": 8.0,
                "expected_kwh_year": 11200,
                "tier_code": "T160",
            },
        }
        mock_size.return_value = sizing_results

        economics_results = {
            "base": {
                "economics_id": str(uuid.uuid4()),
                "roi": 0.15,
                "payback_months": 60,
                "tir": 0.22,
            },
            "plus": {
                "economics_id": str(uuid.uuid4()),
                "roi": 0.18,
                "payback_months": 48,
                "tir": 0.25,
            },
            "pro": {
                "economics_id": str(uuid.uuid4()),
                "roi": 0.20,
                "payback_months": 42,
                "tir": 0.28,
            },
        }

        # Mock de economics para cada tier
        mock_economics.side_effect = [
            economics_results["base"],
            economics_results["plus"],
            economics_results["pro"],
        ]

        recommendations = {
            "recommendation_id": str(uuid.uuid4()),
            "lead_id": lead_id,
            "recommendations": [
                {
                    "tier": "base",
                    "tier_code": "T100",
                    "band_code": "S",
                    "kwp": 5.0,
                    "expected_kwh_year": 7000,
                    "economics": economics_results["base"],
                },
                {
                    "tier": "plus",
                    "tier_code": "T130",
                    "band_code": "M",
                    "kwp": 6.5,
                    "expected_kwh_year": 9100,
                    "economics": economics_results["plus"],
                },
                {
                    "tier": "pro",
                    "tier_code": "T160",
                    "band_code": "L",
                    "kwp": 8.0,
                    "expected_kwh_year": 11200,
                    "economics": economics_results["pro"],
                },
            ],
            "preferred_tier": "plus",
        }
        mock_recommendations.return_value = recommendations

        mock_emit.return_value = {"status": "emitted", "event_type": ""}

        # Act
        result = await agent.orchestrate_pre_process(lead_data, consumption_data, preferences)

        # Assert
        assert mock_create_lead.called
        assert mock_classify.called
        assert mock_select_modality.called
        assert mock_viability.called
        assert mock_size.called
        assert mock_economics.call_count == 3  # Uma vez para cada tier
        assert mock_recommendations.called
        assert mock_emit.call_count >= 4  # Pelo menos 4 eventos devem ser emitidos

        assert "lead" in result
        assert "classification" in result
        assert "modality" in result
        assert "viability" in result
        assert "sizing" in result
        assert "economics" in result
        assert "recommendations" in result
        assert "events" in result

        assert result["lead"]["lead_id"] == lead_id
        assert len(result["recommendations"]["recommendations"]) == 3
        assert len(result["events"]) >= 4        assert len(result["events"]) >= 4
