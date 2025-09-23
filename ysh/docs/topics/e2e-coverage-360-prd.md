# AP2 End-to-End 360° Coverage — Product Requirements Document

## 1. Vision and Context

The Agent Payments Protocol (AP2) repository demonstrates full-stack shopping and payments experiences orchestrated by collaborating agents. This PRD codifies the target state for an end-to-end, 360° coverage suite that spans from lead origination in the PRE domain through checkout finalization and post-payment observability.

- **Product scope**: ensure parity across Android and Python shopping assistants, MCP/A2A agents, and PRE services while keeping the `ap2.e2e360.suite` manifest as the single source of truth for orchestration.
- **Related domains**: Payments (shopping, merchant, credentials provider, processor agents) and Origination & Viability (FastAPI services, NATS event bridge, Kestra playbooks).

## 2. Objectives and Key Results

| Objective | Key Results |
| --- | --- |
| Guarantee seamless, end-to-end validation from lead capture to payment receipt | p95 `checkout_latency_ms` ≤ 5s, p95 `viability_latency_ms` ≤ 3s |
| Maintain frictionless authentication and fraud controls | `otp_retry_count` ≤ 3 across journeys |
| Preserve reliable messaging between PRE and AP2 | Zero `nats_publish_errors` when PRE and AP2 suites run sequentially |
| Increase PRE funnel efficiency | Consistent MQL→SQL conversion rates and accurate bundle recommendations |

## 3. Personas and Jobs-to-Be-Done

- **Residential or commercial lead**: simulates energy potential and financing, receives three curated proposals (kit, financing, integrator) plus upsell paths.
- **PRE analyst**: prioritizes premium leads, validates compliance (LGPD, GD rules), and unblocks only viable opportunities.
- **Shopping agent**: assembles carts, captures intent, and guides OTP challenges using conversational UX.
- **Credentials and processing agents**: tokenize payment methods, orchestrate mandates, and clear authorizations with fallbacks for verification failures.

## 4. Scope Definition

### In scope

- MCP journeys: `human_present`, `human_absent`, and `enable_payment_method` with deterministic logs, events, and metrics as defined in the suite manifest.
- PRE funnel: lead intake, classification, geo enrichment, sizing, bundle recommendation, and NATS publication of `lead.*`, `viability.*`, and `recommendation.bundle.created.v1` events.
- Integration with catalog and finance APIs plus Kestra workflows for automation and 360° health checks.

### Out of scope

- External partner implementations outside declared A2A/MCP contracts.
- Publishing the `ap2/types` package to PyPI (tracked separately on the roadmap).

## 5. Architecture Overview

1. **Origination (PRE)**: FastAPI endpoints capture leads, enforce consent, and publish `lead.captured.v1`. Kestra flows enrich data, perform GD rule checks, compute sizing, and produce recommended bundles.
2. **Event bridge**: NATS subjects (`pre_event_bridge`) emit `lead_captured`, `profile_detected`, `sized`, and `recommendation.bundle.created.v1` events that trigger AP2 suites.
3. **AP2 checkout**: shopping agent initializes intents, merchant agent synchronizes carts, credentials provider tokenizes methods, payment processor applies authentication challenges (OTP, mandate), and merchant issues receipts. The `.logs/watch.log` file provides the canonical audit trail for each `context_id`.

## 6. Functional Requirements

### 6.1 Origination and Pre-Sales

- **Capture and consent**: `POST /leads` creates a unique lead, validates consent, and emits `lead.captured.v1`. Duplicate submissions return HTTP 409.
- **Classification and profiling**: PRE services enrich leads with consumption attributes, then publish `profile_detected` including load factors and tier recommendations.
- **Geo KPIs**: persist GeoJSON payloads keyed by CPF, postal code, and coordinates; reject duplicates with conflict responses.
- **Modalities and allocation**: track SCEE modality, assign internal members, and emit modality events for governance.
- **Sizing and recommendation**: compute kWp tiers, map bundles from band XPP→XGG, emit `sized` and `recommendation.bundle.created.v1`, and annotate upsell candidates.

### 6.2 Payment Flows (AP2)

- **Human-present**: follow steps 1–9 of the MCP playbook, covering intent creation, cart sync, tokenization, OTP challenge, and final receipt with `ap2.checkout.completed.v1`. Handle retries for invalid OTP, authorization declines, or consent revocations.
- **Human-absent**: manage mandates with TTL, asynchronous callbacks, offline validation, and appropriate completion or decline events.
- **Payment method enablement**: validate acceptance criteria, tokenize credentials, sign mandates, and publish `ap2.credential.tokenized.v1`.
- **External APIs**: expose finance catalog via OpenAPI for multi-product proposals, ensuring compatibility with PRE sizing outputs.

## 7. Data Contracts and Integrations

- Maintain JSON Schemas for PRE↔AP2 events (leads, sizing, recommendations, checkout) to guarantee multi-team alignment.
- Share in-memory `risk_memory_store`, the `pre_event_bridge` NATS subjects, and `.logs/watch.log` for cross-squad observability.
- Codify Kestra workflows for merchant, credentials provider, and processor agents to orchestrate HTTP calls and correlate transaction identifiers.

## 8. Observability and Diagnostics

- **Logging**: emit structured logs to `.logs/watch.log` and PRE log stores, both keyed by `context_id` for traceability.
- **Metrics**: track defined latency targets, OTP retries, and NATS error rates. Block release if p95 targets regress or retries exceed thresholds.
- **360° checklist**: automate validation of correlated events, absence of NATS errors, and sequential execution of PRE then AP2 suites within a shared `context_id`.

## 9. Security, Compliance, and Privacy

- Enforce consent collection and retention of personally identifiable information (CPF, address) in compliance with LGPD.
- Tokenization and mandate signature flows must require explicit consent and limit OTP retries to three attempts to prevent abuse.
- Ensure each agent operates under explicit A2A/MCP contracts, enabling secure substitution by heterogeneous implementations.

## 10. Non-Functional Requirements

- **Performance**: honor latency SLOs and support horizontal execution of multiple contexts without log retention breaches.
- **Reliability**: forbid NATS publication failures; allow idempotent event replays without duplicate recommendations.
- **Portability**: rely on manifest-driven orchestration so partner teams can implement protocol-compliant agents in any language.

## 11. Test and Coverage Strategy

1. **Automated PRE suites**: run `pre.e2e.*` workflows per release candidate to validate sizing, geo KPIs, and recommendations before triggering AP2 checkout.
2. **AP2 end-to-end suites**: execute the three MCP playbooks, verify receipts, watch logs, and metric capture, and confirm PRE event correlation via `context_id`.
3. **Contract validation**: lint JSON Schemas and OpenAPI definitions for PRE and finance APIs; fail builds when schema drift occurs.
4. **Manual assisted review**: apply checklist to inspect OTP retries, NATS health, and manifest completeness before sign-off.

## 12. Launch and Operational Playbooks

- **Environments**: run locally with `uv run` scripts for agents and MCP endpoints; mirror flows in staging and production per OpenAPI base URLs.
- **Operational cadence**: start agents with MCP enabled, execute PRE then AP2 suites on the same `context_id`, and publish artifacts (logs, metrics) to observability pipelines.
- **Governance**: keep `dependencies.suites` synchronized between PRE and AP2 squads, and review manifests during change management meetings.

## 13. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| NATS bridge failures | Checkout loses PRE context, breaking recommendations | Monitor `nats_publish_errors`, add alerts, and enable idempotent replays |
| Duplicate Geo data for the same CPF | Incorrect recommendations or LGPD violations | Enforce composite key validation and return HTTP 409 conflicts |
| Excessive OTP retries | Fraud risk and degraded UX | Enforce retry cap, trigger manual review after third failure |
| Schema divergence between squads | Interoperability failures | Version manifests and schemas; integrate schema validation into CI |

## 14. Open Questions

1. Should utility and financing APIs be integrated with live data or staged mocks for early rollouts?
2. What long-term storage strategy is required for `.logs/watch.log` to support audit requirements?
3. When should the `ap2/types` package graduate to PyPI for third-party adoption, and what compatibility guarantees are required?
