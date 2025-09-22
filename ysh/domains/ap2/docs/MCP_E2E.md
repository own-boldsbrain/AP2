# MCP E2E — AP2 Payments 360°

O manifesto [`ap2.e2e360.suite.json`](../mcp/manifests/ap2.e2e360.suite.json) consolida todo o blueprint AP2 para compras com agentes. Ele documenta as dependências entre Shopping Agent, Merchant, Credentials Provider e Payment Processor, além de definir três playbooks MCP:

1. **`ap2.e2e.human_present_checkout`** – fluxo humano-presente ponta-a-ponta (intent → carrinho → tokenização → OTP → recibo) com watch.log e métricas de latência.
2. **`ap2.e2e.human_absent_checkout`** – delega Intent Mandate, monta carrinho offline e usa callbacks para concluir o pagamento em ausência humana.
3. **`ap2.e2e.enable_payment_method`** – ativa/tokeniza métodos compatíveis com o comerciante e emite o evento `ap2.credential.tokenized.v1`.

Cada playbook referencia explicitamente os delegates MCP/A2A que precisam ser encadeados, garantindo rastreabilidade 360° e facilitando os testes E2E descritos no PRD. O manifesto também lista eventos publicados/consumidos e os indicadores de observabilidade (watch.log, latência, contagem de OTPs).

## Como executar no testbed local

1. **Iniciar agentes A2A/MCP**: utilize os scripts `uv run --package ap2-samples python -m roles.<agent>` descritos em `ysh/core/python/scenarios` para subir shopping, merchant, credentials e processor.
2. **Ativar o servidor MCP (FastAPI)**: cada agente expõe `POST /mcp/<agent>` conforme descrito no manifesto. Ao rodar os serviços Python, utilize o parâmetro `--enable-mcp` para abrir o endpoint MCP paralelo ao A2A.
3. **Chamar o playbook**: envie um POST para `http://localhost:8000/mcp/shopping_agent` (ou para o gateway orquestrador) com o corpo do manifesto correspondente. As respostas devem conter recibos, mandates e caminhos de log apontados no manifesto.
4. **Verificar observabilidade**: abra `.logs/watch.log` para validar as entradas de cada passo, e monitore as métricas agregadas (latência total e número de tentativas OTP) conforme metas do manifesto.

> 📌 O manifesto serve como contrato `contract-first` para qualquer agente MCP compatível, permitindo que outros squads implementem os mesmos fluxos em diferentes linguagens sem perder conformidade com o protocolo AP2.
