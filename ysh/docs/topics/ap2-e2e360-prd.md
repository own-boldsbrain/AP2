# PRD — Suíte E2E 360° do Agent Payments Protocol (AP2)

## 1. Visão Geral

O Agent Payments Protocol (AP2) oferece amostras e agentes de demonstração que cobrem jornadas de compra presenciais e automatizadas. Os fluxos são distribuídos entre agentes Android e Python, cada qual com seus respectivos scripts `run.sh` para execução ponta a ponta. Para garantir uma cobertura 360° em máxima performance e eficácia, o manifesto `ap2.e2e360.suite` orquestra Shopping Agent, Merchant, Credentials Provider e Payment Processor, conectando-se com fluxos MCP para descrever intenções, carrinho, credenciais e telemetria completa.

## 2. Problema e Contexto

Precisamos validar continuamente os fluxos de checkout do AP2 (humano-presente, humano-ausente e habilitação de credenciais) do ponto de intenção até o recibo, correlacionando eventos e métricas entre os domínios de Originação (PRE) e Pagamentos. O PRD PRE existente já exige acurácia regulatória de captação, viabilidade e propostas; a suíte AP2 deve herdar esses requisitos para assegurar diagnósticos combinados. Sem essa validação integrada, o risco de regressões silenciosas, perda de rastreabilidade e baixa qualidade operacional aumenta significativamente.

## 3. Objetivos e KPIs

1. **Cobertura funcional completa** dos três playbooks MCP (`human_present_checkout`, `human_absent_checkout`, `enable_payment_method`).
2. **Correlação PRE ↔ AP2** através do `pre_event_bridge` e coexecução da suíte `pre.e2e360.suite`.
3. **Metas de observabilidade**:
   - `checkout_latency_ms` p95 ≤ 5 s;
   - `viability_latency_ms` p95 ≤ 3 s;
   - `nats_publish_errors` = 0;
   - `otp_retry_count` ≤ 3.
4. **Rastreabilidade 360°** com logs estruturados e checklist automatizado que preserva `context_id` contínuo em todo o fluxo.

## 4. Stakeholders e Personas

- **Squad de Pagamentos AP2** — mantêm os agentes Shopping/Merchant/Credentials/Processor e garantem compliance de eventos.
- **Squad PRE (Origination-Viabilidade)** — responsáveis pelos dados de viabilidade e recomendações consumidos pelo checkout.
- **Qualidade e Observabilidade** — operam o `watch.log`, logs do orquestrador PRE e monitoram métricas e alertas.
- **Parceiros externos** — integram novos agentes compatíveis com o manifesto contract-first e validam aderência.

## 5. Escopo Funcional

### 5.1 Fluxo Humano-Presente

- Geração de `IntentMandate`, atualização do carrinho, tokenização e desafio OTP até recibo aprovado.
- Critérios de sucesso: `receipt.status == 'APPROVED'` e emissão do evento `ap2.checkout.completed.v1`.

### 5.2 Fluxo Humano-Não-Presente

- Mandatos com TTL, construção de `CartBlueprint`, callbacks assíncronos e autorização diferida.
- Critérios de sucesso: callbacks finalizados dentro do TTL do `PaymentMandate` e conformidade dos eventos `ap2.checkout.*`.

### 5.3 Habilitação de Métodos de Pagamento

- Validação com o Merchant, listagem de métodos elegíveis, tokenização e assinatura do `PaymentMandate`.
- Critérios de sucesso: emissão de `ap2.credential.tokenized.v1` quando aplicável e confirmação de método habilitado.

### 5.4 Eventos e Telemetria

- Publicação e consumo dos tópicos `ap2.intent.created.v1`, `ap2.checkout.*`, `ap2.credential.tokenized.v1`.
- Amostragem de métricas-chave (`checkout_latency_ms`, `otp_retry_count`, `viability_latency_ms`) com agregação por `context_id`.

## 6. Fora de Escopo

- Criação de agentes fora dos manifestos fornecidos (integração apenas via contrato MCP existente).
- Suporte a esquemas de pagamento adicionais não previstos (`CARD`, `PIX`, `WALLET`).
- Alterações na jornada de originação além do que já foi definido no PRD PRE.

## 7. Requisitos Não Funcionais

### 7.1 Observabilidade

- Logs estruturados com retenção por cenário.
- Propagação de `context_id` entre AP2 e PRE.
- Dashboards com visão em tempo real dos KPIs definidos.

### 7.2 Resiliência

- Monitoramento de `nats_publish_errors` e falhas OTP como critérios de bloqueio GO/NO-GO.
- Retentativas automáticas configuráveis para publicação de eventos críticos.

### 7.3 Compliance

- Consentimento explícito para tokenização e armazenamento seguro de `risk_data`.
- Auditoria automatizada dos eventos de credencial e pagamento.

### 7.4 Expansibilidade

- Manifesto contract-first permite adoção por outras linguagens/plataformas.
- Documentação de exemplos e contratos para parceiros externos.

## 8. Plano de Experimentos e Validação

### 8.1 Preparação

1. Instanciar agentes com `uv run --package ap2-samples python -m roles.<agent> --enable-mcp`.
2. Iniciar o servidor MCP e configurar o `pre_event_bridge` (NATS) com dependências da suíte PRE.
3. Provisionar ambientes com dados sintéticos controlados para permitir repetibilidade.

### 8.2 Execução 360°

1. Disparar playbooks `ap2.e2e.*` seguidos de `pre.e2e.*` no mesmo `context_id`.
2. Validar checklist automatizado que cobre contexto, eventos e tolerância a erros.
3. Registrar artefatos (logs, métricas, recibos) atrelados ao `context_id` para rastreabilidade.

### 8.3 Automação

- Encapsular a execução em workflow `run_ap2_pre_360` com coleta automática de métricas/logs.
- Disponibilizar relatórios diários em canal compartilhado (Data Studio / Looker) para monitoramento contínuo.

### 8.4 Critérios de Aceite

- Todos os delegates executam sem falhas.
- `watch.log` e logs PRE sincronizados e anexados ao relatório automático.
- Métricas dentro das metas definidas e ausência de alertas críticos.

## 9. Roadmap e Entregas

| Fase | Entrega | Indicadores |
| --- | --- | --- |
| **Sprint 1** | Automação dos três playbooks AP2 com coleta de `watch.log` e métricas básicas. | Execução manual em CI com captura de `checkout_latency_ms` e `otp_retry_count`. |
| **Sprint 2** | Integração PRE ↔ AP2 (NATS bridge, execução encadeada) e checklist automatizado. | Registro de `viability_latency_ms` e `nats_publish_errors = 0`. |
| **Sprint 3** | Gate de observabilidade/qualidade pré-deploy com alertas e dashboards compartilhados. | Workflow `run_ap2_pre_360` com saída versionada e logs correlacionados. |

## 10. Riscos e Mitigações

- **Falhas em agentes legados** — padronizar testes com manifesto contract-first para isolar regressões por agente.
- **Descompasso PRE/AP2** — utilizar `context_id` único e alertas quando eventos esperados não chegarem ao NATS bridge.
- **Observabilidade insuficiente** — rever periodicamente a retenção de logs e a cobertura das métricas-alvo para evitar pontos cegos.
- **Dependências externas instáveis** — manter mocks certificados para credenciais e processadores durante execuções críticas.

## 11. Referências

- Guia do repositório e estrutura de cenários: `README.md`.
- Manifesto MCP e orientações de execução: `MCP_E2E` e `ap2.e2e360.suite`.
- Contexto PRE 360°: PRD de Originação.
