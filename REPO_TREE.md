# Repository Tree

ysh/
└─ domains/
   └─ origination-viabilidade/
      ├─ apps/
      │  ├─ origination_api/
      │  │  ├─ app/
      │  │  │  ├─ core/
      │  │  │  │  ├─ config.py
      │  │  │  │  └─ db.py
      │  │  │  ├─ events/
      │  │  │  │  └─ nats_bus.py
      │  │  │  ├─ models/
      │  │  │  │  └─ leads.py
      │  │  │  ├─ routers/
      │  │  │  │  └─ leads.py
      │  │  │  ├─ schemas/
      │  │  │  │  └─ leads.py
      │  │  │  ├─ services/
      │  │  │  │  ├─ sizing.py
      │  │  │  │  └─ recommendations.py
      │  │  │  └─ main.py
      │  │  ├─ configs/
      │  │  │  ├─ project_size_bands.yaml
      │  │  │  ├─ recommendation_tiers.yaml
      │  │  │  ├─ upsell_rules.yaml
      │  │  │  └─ scee.modalidades.json
      │  │  ├─ contracts/
      │  │  │  ├─ openapi.yaml
      │  │  │  └─ asyncapi.yaml
      │  │  ├─ tests/
      │  │  │  └─ test_health.py
      │  │  ├─ Dockerfile
      │  │  ├─ docker-compose.yml
      │  │  ├─ pyproject.toml
      │  │  └─ .env.example
      │  ├─ viability_service/
      │  │  ├─ app/
      │  │  │  ├─ main.py
      │  │  │  ├─ services/
      │  │  │  │  ├─ viability.py
      │  │  │  │  └─ economics.py
      │  │  │  └─ events/nats_bus.py
      │  │  ├─ pyproject.toml
      │  │  ├─ Dockerfile
      │  │  └─ .env.example
      │  ├─ aneel_tariffs/
      │  │  ├─ app/main.py
      │  │  ├─ pyproject.toml
      │  │  ├─ Dockerfile
      │  │  └─ .env.example
      │  ├─ aneel_kpis/
      │  │  ├─ app/main.py
      │  │  ├─ pyproject.toml
      │  │  ├─ Dockerfile
      │  │  └─ .env.example
      │  ├─ aneel_utilities/
      │  │  ├─ app/main.py
      │  │  ├─ pyproject.toml
      │  │  ├─ Dockerfile
      │  │  └─ .env.example
      │  └─ docker-compose.stack.yml
      ├─ mcp/
      │  └─ manifests/
      │     ├─ solar.viability.agent.json
      │     ├─ aneel.tariffs.agent.json
      │     ├─ aneel.kpis.agent.json
      │     └─ aneel.utilities.agent.json
      ├─ workflows/
      │  ├─ kestra/
      │  │  ├─ lead_intake_enrich_score.yaml
      │  │  ├─ profile_enrichment.yaml
      │  │  ├─ sizing_and_recommendations.yaml
      │  │  └─ viability_and_economics.yaml
      │  └─ nodered/
      │     └─ inbound_webhooks_leads.json
      ├─ data/
      │  └─ schemas/
      │     ├─ postgres_ysh_leads.sql
      │     ├─ postgres_features.sql
      │     ├─ postgres_reco_bands.sql
      │     └─ clickhouse_calc_sizing.sql
      ├─ dashboards/
      │  ├─ kpis_origination.yaml
      │  ├─ kpis_segmentation.yaml
      │  └─ kpis_reco.yaml
      ├─ contracts/
      │  └─ events/
      │     ├─ lead.captured.v1.schema.json
      │     ├─ lead.scored.v1.schema.json
      │     ├─ system.sized.v1.schema.json
      │     ├─ consumption.profile.detected.v1.schema.json
      │     ├─ generation.modality.selected.v1.schema.json
      │     ├─ recommendation.bundle.created.v1.schema.json
      │     ├─ viability.requested.v1.schema.json
      │     └─ viability.completed.v1.schema.json
      ├─ docs/
      │  ├─ PRD_Origination_360.md
      │  ├─ JTBDs.md
      │  ├─ SIZING_RULES.md
      │  ├─ PLAYBOOK_RECOMENDACOES.md
      │  └─ WIRES_MCP.md
      ├─ OWNERS.yml
      ├─ SLA.md
      └─ README.
