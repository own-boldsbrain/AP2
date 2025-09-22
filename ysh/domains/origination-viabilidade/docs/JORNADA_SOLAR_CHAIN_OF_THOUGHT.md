# Jornada Solar Personalizada — Fases × Tools × Tasks Interact

## Visão Geral
A suíte `pre.e2e360.suite` encadeia o ciclo de captação, viabilidade e recomendações e já lista dependências MCP para cálculos solares, tarifas ANEEL e eventos NATS, formando a espinha dorsal da jornada personalizada.【F:ysh/domains/origination-viabilidade/mcp/manifests/pre.e2e360.suite.json†L1-L169】
Os objetivos declarados no PRD e nos JTBDs reforçam a necessidade de entregar três ofertas baseadas em dados regulatórios, priorizar leads premium e atender às regras GD para cada concessão.【F:ysh/domains/origination-viabilidade/docs/PRD_Origination_360.md†L1-L5】【F:ysh/domains/origination-viabilidade/docs/JTBDs.md†L1-L3】

## Canvas Chain-of-Thought para as Fases
Para tornar o blueprint navegável por squads de produto, use o componente `ChainOfThought` como contêiner visual das fases. Ele pode receber ícones customizados e estados de conclusão, permitindo ligar cada step aos delegates do manifesto MCP.

```tsx
import {
  ChainOfThought,
  ChainOfThoughtContent,
  ChainOfThoughtHeader,
  ChainOfThoughtStep,
  ChainOfThoughtSearchResults,
  ChainOfThoughtSearchResult,
} from '@/components/ai-elements/chain-of-thought';

<ChainOfThought defaultOpen>
  <ChainOfThoughtHeader>Jornada Solar Personalizada</ChainOfThoughtHeader>
  <ChainOfThoughtContent>
    <ChainOfThoughtStep label="Onboarding & Consentimento" status="complete">
      <ChainOfThoughtSearchResults>
        <ChainOfThoughtSearchResult>
          pre_orchestrator_agent.create_update_lead
        </ChainOfThoughtSearchResult>
        <ChainOfThoughtSearchResult>
          Form LeadCreate + ClassifyIn
        </ChainOfThoughtSearchResult>
      </ChainOfThoughtSearchResults>
    </ChainOfThoughtStep>
    <ChainOfThoughtStep label="Viabilidade Técnica" status="active">
      <ChainOfThoughtSearchResults>
        <ChainOfThoughtSearchResult>
          solar_viability.agent.viability.compute
        </ChainOfThoughtSearchResult>
        <ChainOfThoughtSearchResult>
          viability.completed.v1
        </ChainOfThoughtSearchResult>
      </ChainOfThoughtSearchResults>
    </ChainOfThoughtStep>
    <ChainOfThoughtStep label="Recomendações & Upsell" status="pending">
      <ChainOfThoughtSearchResults>
        <ChainOfThoughtSearchResult>
          recommendation.bundle.created.v1
        </ChainOfThoughtSearchResult>
        <ChainOfThoughtSearchResult>
          Artifact Service /proposals
        </ChainOfThoughtSearchResult>
      </ChainOfThoughtSearchResults>
    </ChainOfThoughtStep>
  </ChainOfThoughtContent>
</ChainOfThought>
```

### Boas práticas de instrumentação
- Marque cada `ChainOfThoughtStep` com o `context_id` vindo do manifesto MCP para facilitar a correlação de logs e métricas.
- Use badges extras para destacar upsells disparados pelas regras ou eventos opcionais (ex.: cross-sell AP2 via `pre_event_bridge`).【F:ysh/domains/ap2/mcp/manifests/ap2.e2e360.suite.json†L77-L93】

## Combinação Fases × Tools × Tasks Interact
A tabela abaixo consolida quais componentes UI, agentes MCP e tarefas interativas devem ser ativados em cada fase. Ela também destaca artefatos/eventos e métricas de observabilidade para manter a personalização alinhada às metas.

| Fase | Objetivo & Dados | Tools MCP / Serviços | Tasks Interact & Eventos | Observabilidade |
| --- | --- | --- | --- | --- |
| **1. Onboarding & Consentimento** | Captar lead com consentimento LGPD, classe tarifária e preferências usando os esquemas `LeadCreate`, `ClassifyIn` e `ModalityIn`. | `pre_orchestrator_agent.create_update_lead` e `classify_consumer` garantem persistência e classificação do lead com tarificação correta.【F:ysh/domains/origination-viabilidade/apps/origination_api/app/schemas/leads.py†L6-L61】【F:ysh/domains/origination-viabilidade/mcp/manifests/pre_orchestrator_agent.json†L15-L137】 | UI dispara o tool `pre.e2e.orchestrate_pipeline` (step 1-3) para acionar criação do lead, classificação e seleção de modalidade, emitindo `viability.requested.v1` com lat/long para cálculo posterior.【F:ysh/domains/origination-viabilidade/mcp/manifests/pre.e2e360.suite.json†L123-L157】【F:ysh/domains/origination-viabilidade/contracts/events/viability.requested.v1.schema.json†L1-L14】 | Monitorar MQL→SQL, consentimento captado e SLA de ingestão≤5min.【F:ysh/domains/origination-viabilidade/dashboards/kpis_origination.yaml†L1-L7】【F:ysh/domains/origination-viabilidade/SLA.md†L1-L7】 |
| **2. Segmentação & Dados Regulatórios** | Enriquecer consumo e aplicar regras GD (bandas XPP→XGG, tiers). | Delegates `classify_consumer` + `aneel.utilities.agent`/`aneel.tariffs.agent` adicionados como dependências MCP para perfis tarifários e catálogos.【F:ysh/domains/origination-viabilidade/mcp/manifests/pre.e2e360.suite.json†L24-L68】 | Tasks 3-5 do playbook constroem `tariff_profile` e preparam features de dimensionamento, alimentando dashboards segmentados por persona/cluster.【F:ysh/domains/origination-viabilidade/mcp/manifests/pre.e2e360.suite.json†L135-L148】【F:ysh/domains/origination-viabilidade/dashboards/kpis_segmentation.yaml†L1-L7】 | Acompanhar latência NATS entre `viability.requested` e `viability.completed`, além de KPIs por cluster.【F:ysh/domains/origination-viabilidade/docs/WIRES_MCP.md†L1-L9】 |
| **3. Viabilidade Técnica & Econômica** | Calcular geração kWh/ano, PR e indicadores financeiros alinhados às regras de dimensionamento.【F:ysh/domains/origination-viabilidade/docs/SIZING_RULES.md†L1-L3】 | `solar_viability.agent.viability.compute` usa pvlib/NASA e `solar_viability.agent.economics.evaluate` aplica ROI/Payback/TIR sobre perfis tarifários.【F:ysh/domains/origination-viabilidade/mcp/manifests/pre.e2e360.suite.json†L140-L153】【F:ysh/domains/origination-viabilidade/apps/viability_service/app/services/viability.py†L24-L45】【F:ysh/domains/origination-viabilidade/apps/viability_service/app/services/economics.py†L1-L97】 | UI exibe resultados intermediários através do componente `ChainOfThought`, destacando a publicação de `viability.completed.v1` e métricas de economics retornadas pelo tool.【F:ysh/domains/origination-viabilidade/contracts/events/viability.completed.v1.schema.json†L1-L15】 | Checar metas de payback/TIR>0 e SLA de proposta p95≤10min; registrar PR e perdas em dashboards.【F:ysh/domains/origination-viabilidade/SLA.md†L1-L7】【F:ysh/domains/origination-viabilidade/dashboards/kpis_reco.yaml†L1-L7】 |
| **4. Recomendações & Upsell** | Gerar kits Base/Plus/Pro com upsell contextual, mapear kWp para banda e anexar proposta. | Serviço de sizing escolhe banda e `recommendations.build_bundle` aplica tiers (T115–T160) e regras de upsell configuradas em YAML.【F:ysh/domains/origination-viabilidade/apps/origination_api/app/services/sizing.py†L1-L57】【F:ysh/domains/origination-viabilidade/apps/origination_api/app/services/recommendations.py†L1-L98】【F:ysh/domains/origination-viabilidade/apps/origination_api/configs/project_size_bands.yaml†L1-L9】【F:ysh/domains/origination-viabilidade/apps/origination_api/configs/recommendation_tiers.yaml†L1-L5】【F:ysh/domains/origination-viabilidade/apps/origination_api/configs/upsell_rules.yaml†L1-L6】 | Task 7 do playbook emite `recommendation.bundle.created.v1`, ativa o Artifact Service `/proposals` para armazenar anexos e prepara o handoff AP2.【F:ysh/domains/origination-viabilidade/mcp/manifests/pre.e2e360.suite.json†L155-L157】【F:ysh/domains/origination-viabilidade/contracts/events/recommendation.bundle.created.v1.schema.json†L1-L27】【F:ysh/domains/origination-viabilidade/apps/artifact_service/app/main.py†L21-L113】 | Medir `tier_mix_share`, `upsell_attach_rate` e tempo até proposta; validar anexos disponíveis para download.【F:ysh/domains/origination-viabilidade/dashboards/kpis_reco.yaml†L1-L7】 |
| **5. Ativação Financeira & Cross-Sell AP2** | Disparar jornada de pagamento humano-presente e sincronizar eventos PRE ↔ AP2 pelo bridge NATS. | Suite `ap2.e2e360.suite` depende do `pre_event_bridge` e do tool `ap2.e2e.human_present_checkout` para conduzir mandato, tokenização e recibo.【F:ysh/domains/ap2/mcp/manifests/ap2.e2e360.suite.json†L1-L199】 | Tasks Interact iniciam o checkout usando pacotes recomendados como carrinho, correlacionando `recommendation.bundle.created.v1` com recibos AP2 via bridge.【F:ysh/domains/ap2/docs/MCP_E2E.md†L3-L27】 | Auditar `.logs/watch.log`, `viability_latency_ms`, `otp_retry_count` e reconciliar eventos esperados para garantir a personalização financeira.【F:ysh/domains/ap2/docs/MCP_E2E.md†L11-L36】 |
| **6. Diagnóstico Contínuo & Re-engajamento** | Monitorar SLAs, reativar leads e rodar campanhas baseadas em KPIs segmentados. | Dashboards globais e segmentados (originação, recomendações) fornecem sinais para tasks de reengajamento; SLA define limites de latência e disponibilidade.【F:ysh/domains/origination-viabilidade/dashboards/kpis_origination.yaml†L1-L7】【F:ysh/domains/origination-viabilidade/dashboards/kpis_segmentation.yaml†L1-L7】【F:ysh/domains/origination-viabilidade/SLA.md†L1-L8】 | Tasks Interact executam playbooks de retomada (ex.: `pre.e2e.orchestrate_pipeline` com leads reativados) e usam wires MCP documentados para campanhas e cross-sell.【F:ysh/domains/origination-viabilidade/docs/WIRES_MCP.md†L1-L9】 | KPIs como `reactivation_rate`, `lead_premium_rate` e `upsell_bateria_rate` alimentam alertas e trilhas de experimentação.【F:ysh/domains/origination-viabilidade/dashboards/kpis_origination.yaml†L1-L7】【F:ysh/domains/origination-viabilidade/dashboards/kpis_segmentation.yaml†L1-L7】 |

## Plano de Cobertura 360° E2E 1:1
O plano a seguir garante que cada lead percorra a jornada ponta a ponta com verificações 1:1 entre entrada, eventos publicados e entregáveis das suítes PRE e AP2. Ele combina cenários felizes, variações de dados regulatórios e falhas controladas para validar o comportamento resiliente das APIs.

### Pilar 1 — Preparação de Dados & Fixtures
- **Identidade do lead:** Gerar fixtures que cubram classes tarifárias residenciais e comerciais, incluindo variação de faixa de consumo (`ClassifyIn`) e coordenadas com e sem cobertura satelital, armazenando-as no catálogo de testes (`tests/fixtures/leads/*.json`).
- **Tarifas & catálogos:** Versionar snapshots ANEEL por concessão em `tests/data/aneel/<concessionaria>.json` e configurar o pipeline para selecionar automaticamente o snapshot correspondente ao `context_id` do teste.【F:ysh/domains/origination-viabilidade/mcp/manifests/pre.e2e360.suite.json†L24-L68】
- **Artefatos de saída:** Definir golden files para propostas (`/proposals`) e recibos AP2, assegurando diffs estruturais (`jsondiff`) por fase.【F:ysh/domains/origination-viabilidade/apps/artifact_service/app/main.py†L61-L113】【F:ysh/domains/ap2/docs/MCP_E2E.md†L3-L27】

### Pilar 2 — Cenários E2E Sequenciais
| Cenário | Objetivo | Steps Principais | Métricas/KPIs Validados |
| --- | --- | --- | --- |
| **Happy Path Premium** | Validar lead premium percorrendo 6 fases em <10min. | Executar `pre.e2e.orchestrate_pipeline` com lead premium → aguardar `viability.completed.v1` → gerar bundle com upsell bateria → iniciar `ap2.e2e.human_present_checkout`. | `viability_latency_ms`, `tier_mix_share`, `otp_retry_count`, SLA p95≤10min.【F:ysh/domains/origination-viabilidade/SLA.md†L1-L7】【F:ysh/domains/ap2/docs/MCP_E2E.md†L11-L36】 |
| **GD Edge Cases** | Confirmar aderência regulatória em bandas/tarifas limite. | Variar `aneel.tariffs.agent` com bandeiras XPP/XGG, simular perfil baixa renda e validar regras de dimensionamento.【F:ysh/domains/origination-viabilidade/apps/origination_api/app/services/sizing.py†L1-L57】 | `lead_premium_rate`, `upsell_bateria_rate`, diffs zero em golden files de proposta. |
| **Falha Externa Controlada** | Verificar retentativas quando NASA/ANEEL indisponíveis. | Forçar timeout no consumo NASA via proxy → observar retries do `solar_viability.agent.viability.compute` → garantir retomada até `viability.completed.v1`. | Alarmes de fallback, tempo total da fase 3, ausência de `viability.failed`.|
| **Reengajamento 30 dias** | Assegurar reativação automática pós follow-up. | Reativar lead expirado com `pre.e2e.orchestrate_pipeline` → disparar campanha via wires MCP → confirmar novo bundle e handoff AP2. | `reactivation_rate`, `upsell_attach_rate`, contagem de eventos reemitidos.【F:ysh/domains/origination-viabilidade/docs/WIRES_MCP.md†L1-L9】 |

### Pilar 3 — Telemetria & Alertas 1:1
- **Correlação obrigatória:** Para cada cenário, registrar `context_id`, `lead_id` e `proposal_id` no ChainOfThought, no Artifact Service e no recibo AP2, viabilizando rastreabilidade completa.【F:ysh/domains/origination-viabilidade/docs/JORNADA_SOLAR_CHAIN_OF_THOUGHT.md†L12-L54】
- **Alarmes automáticos:** Configurar alertas que disparem no primeiro desvio (1:1) entre eventos esperados e emitidos—ex.: ausências de `viability.completed.v1` dentro do SLA ou divergência entre total do bundle e recibo AP2.【F:ysh/domains/origination-viabilidade/contracts/events/viability.completed.v1.schema.json†L1-L15】【F:ysh/domains/ap2/mcp/manifests/ap2.e2e360.suite.json†L77-L93】
- **Dashboards 360°:** Atualizar dashboards de originação, segmentação e recomendações com filtros por `context_id` para confirmar cobertura individual e alimentar o playbook de reengajamento.【F:ysh/domains/origination-viabilidade/dashboards/kpis_origination.yaml†L1-L7】【F:ysh/domains/origination-viabilidade/dashboards/kpis_segmentation.yaml†L1-L7】【F:ysh/domains/origination-viabilidade/dashboards/kpis_reco.yaml†L1-L7】

### Pilar 4 — Governança & Automatização
- **Pipeline CI 360°:** Encadear cenários anteriores em job noturno com paralelização por persona (Residencial, Comercial) e publicação automática dos relatórios diffs/golden no Artifact Service.
- **Rotina de revisão:** Revisar mensalmente fixtures ANEEL e regras de upsell; qualquer mudança gera execução ad-hoc da suíte 360° para garantir conformidade imediata.【F:ysh/domains/origination-viabilidade/apps/origination_api/configs/recommendation_tiers.yaml†L1-L5】【F:ysh/domains/origination-viabilidade/apps/origination_api/configs/upsell_rules.yaml†L1-L6】
- **Playbook de resposta:** Documentar passos de rollback e comunicação em caso de falha crítica, reutilizando o manifesto MCP e os badges do ChainOfThought para sinalizar status 1:1 aos stakeholders.【F:ysh/domains/origination-viabilidade/docs/PLAYBOOK_RECOMENDACOES.md†L1-L4】

## Próximos Passos
1. Implementar o componente `ChainOfThought` no cockpit do analista para acompanhar, em tempo real, o status das tasks MCP mencionadas acima.
2. Automatizar a publicação no Artifact Service logo após o delegate de recomendações para disponibilizar PDFs/JSON antes do handoff AP2.【F:ysh/domains/origination-viabilidade/apps/artifact_service/app/main.py†L61-L113】
3. Configurar alertas nos dashboards quando as metas de SLA e KPIs forem ultrapassadas, habilitando rotas automáticas de reengajamento conforme o playbook de recomendações.【F:ysh/domains/origination-viabilidade/SLA.md†L1-L8】【F:ysh/domains/origination-viabilidade/docs/PLAYBOOK_RECOMENDACOES.md†L1-L4】
