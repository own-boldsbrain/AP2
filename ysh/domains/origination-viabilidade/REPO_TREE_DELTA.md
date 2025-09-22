# ysh/domains/origination-viabilidade/REPO_TREE_DELTA.md
ysh/
└─ domains/
   └─ origination-viabilidade/
      ├─ apps/
      │  ├─ origination_api/                      # (já existente) — leads + recomendações
      │  ├─ viability_service/                    # NOVO — pvlib/NASA + economia
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
      │  └─ docker-compose.stack.yml              # NOVO — sobe todos os serviços do domínio
      ├─ mcp/
      │  └─ manifests/
      │     ├─ solar.viability.agent.json
      │     ├─ aneel.tariffs.agent.json
      │     ├─ aneel.kpis.agent.json
      │     └─ aneel.utilities.agent.json
      ├─ contracts/
      │  └─ events/
      │     ├─ viability.requested.v1.schema.json
      │     └─ viability.completed.v1.schema.json
      ├─ workflows/
      │  └─ kestra/
      │     └─ viability_and_economics.yaml       # NOVO — orquestra a cadeia viability→tariffs→economics
      └─ docs/
         └─ WIRES_MCP.md                          # NOVO — exemplos de wiring A2A/MCP
