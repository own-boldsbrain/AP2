# MCP E2E — AP2 Payments 360°

O manifesto [`ap2.e2e360.suite.json`](../mcp/manifests/ap2.e2e360.suite.json) consolida todo o blueprint AP2 para compras com agentes. Ele documenta as dependências entre Shopping Agent, Merchant, Credentials Provider e Payment Processor, além de definir três playbooks MCP:

1. **`ap2.e2e.human_present_checkout`** – fluxo humano-presente ponta-a-ponta (intent → carrinho → tokenização → OTP → recibo) com watch.log e métricas de latência.
2. **`ap2.e2e.human_absent_checkout`** – delega Intent Mandate, monta carrinho offline e usa callbacks para concluir o pagamento em ausência humana.
3. **`ap2.e2e.enable_payment_method`** – ativa/tokeniza métodos compatíveis com o comerciante e emite o evento `ap2.credential.tokenized.v1`.

Cada playbook referencia explicitamente os delegates MCP/A2A que precisam ser encadeados, garantindo rastreabilidade 360° e facilitando os testes E2E descritos no PRD. O manifesto também lista eventos publicados/consumidos e os indicadores de observabilidade (watch.log, latência, contagem de OTPs).

## Integração PRE ↔ AP2 para diagnóstico 360°

A evolução da suíte `ap2.e2e360.suite` adiciona dependências explícitas com o domínio PRE para que a varredura 360° acompanhe todo o funil de originação até o checkout. Os principais incrementos são:

- **Bridge de eventos (`pre_event_bridge`)**: canal NATS compartilhado para correlacionar `viability.*` e `recommendation.bundle.created.v1` com os eventos `ap2.checkout.*`.
- **Referência ao manifesto PRE**: `dependencies.suites` aponta para `pre.e2e360.suite.json`, sinalizando que os playbooks PRE (`pre.e2e.orchestrate_pipeline`, `pre.e2e.evaluate_site`) devem ser executados no mesmo run para cobertura 360°.
- **Métricas combinadas**: `viability_latency_ms` e `nats_publish_errors` foram incorporadas à seção de observabilidade ao lado de `checkout_latency_ms` e `otp_retry_count`.
- **Logs correlacionados**: além do `.logs/watch.log`, a suíte referencia o log estruturado do orquestrador PRE para facilitar a busca pelo mesmo `context_id`.
- **Checklist automatizável**: o bloco `diagnostics` do manifesto documenta as verificações mínimas (correlação de `context_id`, eventos esperados e tolerância a erros).

### Checklist de diagnóstico recomendado

1. Execute `ap2.e2e.*` e, na sequência, `pre.e2e.*`, usando o mesmo `context_id` ou sessão.
2. Confirme que o `pre_event_bridge` publicou `viability.requested.v1`, `viability.completed.v1` e `recommendation.bundle.created.v1`.
3. Valide que `.logs/watch.log` e o log do orquestrador PRE possuem as etapas de todos os delegates.
4. Confira as métricas `checkout_latency_ms`, `otp_retry_count`, `viability_latency_ms` e `nats_publish_errors` contra as metas definidas no manifesto.
5. Antes de aprovar a saúde do cenário, garanta que não houve erro de publicação no NATS e que o fluxo OTP se manteve dentro do limite de tentativas.



## Como executar no testbed local

1. **Iniciar agentes A2A/MCP**: utilize os scripts `uv run --package ap2-samples python -m roles.<agent>` descritos em `ysh/core/python/scenarios` para subir shopping, merchant, credentials e processor.
2. **Ativar o servidor MCP (FastAPI)**: cada agente expõe `POST /mcp/<agent>` conforme descrito no manifesto. Ao rodar os serviços Python, utilize o parâmetro `--enable-mcp` para abrir o endpoint MCP paralelo ao A2A.
3. **Chamar o playbook**: envie um POST para `http://localhost:8000/mcp/shopping_agent` (ou para o gateway orquestrador) com o corpo do manifesto correspondente. As respostas devem conter recibos, mandates e caminhos de log apontados no manifesto.
4. **Verificar observabilidade**: abra `.logs/watch.log` **e** o log do orquestrador PRE (`domains/origination-viabilidade/apps/pre_orchestrator/.logs/server.log`) para validar as entradas de cada passo, e monitore as métricas agregadas (latência total, número de tentativas OTP, `viability_latency_ms` e `nats_publish_errors`) conforme metas do manifesto.

> 📌 O manifesto serve como contrato `contract-first` para qualquer agente MCP compatível, permitindo que outros squads implementem os mesmos fluxos em diferentes linguagens sem perder conformidade com o protocolo AP2.
