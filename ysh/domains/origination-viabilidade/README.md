## Origination & Viabilidade · YSH
API e artefatos para captação de leads, enriquecimento, classificação (classe/UC/perfil), dimensionamento (kWp), recomendações (tiers 115/130/145/160 e bands XPP→XGG) e modalidades SCEE (AUTO_LOCAL/REMOTO/COMPARTILHADA/MUC), com eventos NATS.

### Rodar (dev)
1) `cp apps/origination_api/.env.example apps/origination_api/.env`
2) `docker compose -f apps/origination_api/docker-compose.yml up --build`
3) API: `http://localhost:8000/docs` · OpenAPI: `/openapi.json`
4) NATS: `nats://localhost:4222` · Postgres: `postgres://ysh:secret@localhost:5432/ysh`
