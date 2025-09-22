# Wires (A2A/MCP) — exemplos

1. lead → viability → tariffs → economics → recommendations (ver `pre.e2e360.suite.json`).
2. benchmark distribuidora (INDGER + IASC + Utilities).
3. gatilho de cross-sell AP2 ↔ PRE: `ap2.intent.created.v1` → `pre.e2e.orchestrate_pipeline` (gera `recommendation.bundle.created.v1`).

Contratos de evento: `viability.requested.v1` → `viability.completed.v1` → `recommendation.bundle.created.v1`.

O manifesto [`pre.e2e360.suite.json`](../mcp/manifests/pre.e2e360.suite.json) detalha cada delegate MCP (pvlib, tarifas, economics) e garante observabilidade por métricas de latência e erros NATS.
