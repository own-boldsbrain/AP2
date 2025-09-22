"""
Script de migração para inicializar as tabelas relacionadas ao orquestrador PRE.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

import asyncpg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da conexão
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/yellowsolar"

# Tabelas a serem criadas
TABLES = [
    """
    CREATE TABLE IF NOT EXISTS pre_orchestration (
        id UUID PRIMARY KEY,
        lead_id UUID NOT NULL,
        status VARCHAR(50) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        completed_at TIMESTAMP WITH TIME ZONE,
        preferences JSONB,
        metadata JSONB
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS pre_recommendation (
        id UUID PRIMARY KEY,
        orchestration_id UUID NOT NULL REFERENCES pre_orchestration(id),
        tier VARCHAR(10) NOT NULL,
        tier_code VARCHAR(10) NOT NULL,
        band_code VARCHAR(10) NOT NULL,
        kwp NUMERIC(10, 2) NOT NULL,
        expected_kwh_year NUMERIC(10, 2) NOT NULL,
        is_preferred BOOLEAN NOT NULL DEFAULT FALSE,
        economics JSONB NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        metadata JSONB
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS pre_orchestration_event (
        id UUID PRIMARY KEY,
        orchestration_id UUID NOT NULL REFERENCES pre_orchestration(id),
        event_type VARCHAR(100) NOT NULL,
        payload JSONB NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        emitted_at TIMESTAMP WITH TIME ZONE,
        status VARCHAR(50) NOT NULL DEFAULT 'pending'
    );
    """
]

# Índices a serem criados
INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_pre_orchestration_lead_id ON pre_orchestration(lead_id);",
    "CREATE INDEX IF NOT EXISTS idx_pre_orchestration_status ON pre_orchestration(status);",
    "CREATE INDEX IF NOT EXISTS idx_pre_recommendation_orchestration_id ON pre_recommendation(orchestration_id);",
    "CREATE INDEX IF NOT EXISTS idx_pre_orchestration_event_orchestration_id ON pre_orchestration_event(orchestration_id);",
    "CREATE INDEX IF NOT EXISTS idx_pre_orchestration_event_event_type ON pre_orchestration_event(event_type);",
    "CREATE INDEX IF NOT EXISTS idx_pre_orchestration_event_status ON pre_orchestration_event(status);"
]

# Dados de exemplo para inserção
SAMPLE_DATA: List[Dict[str, Any]] = [
    {
        "table": "pre_orchestration",
        "data": [
            {
                "id": "d5f8d9e0-5f1a-4c7c-9b5c-6f8e7d6c5b4a",
                "lead_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
                "status": "completed",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "completed_at": datetime.now(),
                "preferences": {
                    "has_roof": True,
                    "multiple_ucs": False,
                    "tilt_deg": 20,
                    "azimuth_deg": 180,
                    "preferred_tier": "plus"
                },
                "metadata": {
                    "source": "landing",
                    "campaign": "solar_verao_2025"
                }
            }
        ]
    },
    {
        "table": "pre_recommendation",
        "data": [
            {
                "id": "e6f9e0a1-6f2b-5d8d-0c6d-7f9e8d7c6b5a",
                "orchestration_id": "d5f8d9e0-5f1a-4c7c-9b5c-6f8e7d6c5b4a",
                "tier": "base",
                "tier_code": "T100",
                "band_code": "S",
                "kwp": 5.0,
                "expected_kwh_year": 7000,
                "is_preferred": False,
                "economics": {
                    "roi": 0.15,
                    "payback_months": 60,
                    "tir": 0.22,
                    "capex": 35000
                },
                "created_at": datetime.now(),
                "metadata": None
            },
            {
                "id": "f7a0f1b2-7f3c-6e9e-1d7e-8f0f9e8d7c6b",
                "orchestration_id": "d5f8d9e0-5f1a-4c7c-9b5c-6f8e7d6c5b4a",
                "tier": "plus",
                "tier_code": "T130",
                "band_code": "M",
                "kwp": 6.5,
                "expected_kwh_year": 9100,
                "is_preferred": True,
                "economics": {
                    "roi": 0.18,
                    "payback_months": 48,
                    "tir": 0.25,
                    "capex": 45500
                },
                "created_at": datetime.now(),
                "metadata": None
            },
            {
                "id": "g8b1g2c3-8g4d-7f0f-2e8f-9g1g0f9e8d7c",
                "orchestration_id": "d5f8d9e0-5f1a-4c7c-9b5c-6f8e7d6c5b4a",
                "tier": "pro",
                "tier_code": "T160",
                "band_code": "L",
                "kwp": 8.0,
                "expected_kwh_year": 11200,
                "is_preferred": False,
                "economics": {
                    "roi": 0.20,
                    "payback_months": 42,
                    "tir": 0.28,
                    "capex": 56000
                },
                "created_at": datetime.now(),
                "metadata": None
            }
        ]
    },
    {
        "table": "pre_orchestration_event",
        "data": [
            {
                "id": "h9c2h3d4-9h5e-8g1g-3f9g-0h2h1g0f9e8d",
                "orchestration_id": "d5f8d9e0-5f1a-4c7c-9b5c-6f8e7d6c5b4a",
                "event_type": "lead.captured.v1",
                "payload": {
                    "lead_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
                    "source": "landing",
                    "consent": True
                },
                "created_at": datetime.now(),
                "emitted_at": datetime.now(),
                "status": "emitted"
            },
            {
                "id": "i0d3i4e5-0i6f-9h2h-4g0h-1i3i2h1g0f9e",
                "orchestration_id": "d5f8d9e0-5f1a-4c7c-9b5c-6f8e7d6c5b4a",
                "event_type": "recommendation.bundle.created.v1",
                "payload": {
                    "lead_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
                    "recommendation_id": "e6f9e0a1-6f2b-5d8d-0c6d-7f9e8d7c6b5a",
                    "tier_count": 3,
                    "preferred_tier": "plus"
                },
                "created_at": datetime.now(),
                "emitted_at": datetime.now(),
                "status": "emitted"
            }
        ]
    }
]


async def create_tables(conn: asyncpg.Connection) -> None:
    """Cria as tabelas se não existirem."""
    for table_sql in TABLES:
        await conn.execute(table_sql)
        logger.info(f"Executada criação da tabela: {table_sql.strip().split('(')[0]}")


async def create_indexes(conn: asyncpg.Connection) -> None:
    """Cria os índices se não existirem."""
    for index_sql in INDEXES:
        await conn.execute(index_sql)
        logger.info(f"Executada criação do índice: {index_sql}")


async def insert_sample_data(conn: asyncpg.Connection) -> None:
    """Insere dados de exemplo nas tabelas."""
    for table_data in SAMPLE_DATA:
        table = table_data["table"]
        data = table_data["data"]

        for record in data:
            columns = list(record.keys())
            placeholders = [f'${i + 1}' for i in range(len(columns))]
            values = list(record.values())

            query = f"""
            INSERT INTO {table} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            ON CONFLICT (id) DO NOTHING
            """

            await conn.execute(query, *values)
            logger.info(f'Inserido registro em {table}')


async def main() -> None:
    """Função principal para executar a migração."""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info('Conexão com o banco de dados estabelecida')

        await create_tables(conn)
        await create_indexes(conn)

        # Verifique se as tabelas têm dados antes de inserir dados de exemplo
        count = await conn.fetchval('SELECT COUNT(*) FROM pre_orchestration')
        if count == 0:
            logger.info('Inserindo dados de exemplo...')
            await insert_sample_data(conn)
        else:
            logger.info(
                'Dados já existem, pulando inserção de dados de exemplo'
            )

        await conn.close()
        logger.info("Migração concluída com sucesso")

    except Exception as e:
        logger.error(f"Erro durante a migração: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
