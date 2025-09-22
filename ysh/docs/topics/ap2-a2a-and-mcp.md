# AP2, A2A e MCP

O Protocolo de Pagamentos de Agente (AP2) é projetado para ser uma extensão do protocolo [Agent-to-Agent (A2A)](https://a2a-protocol.org) e trabalhar em conjunto com o [Model-Context Protocol (MCP)](https://modelcontextprotocol.org).

<!-- prettier-ignore-start -->
!!! abstract "Desambiguação de comunicação"

    -   MCP: Agentes se comunicam com dados (APIs)
    -   A2A: Agentes se comunicam com outros Agentes (tarefas e mensagens)
    -   AP2: Agentes se comunicam sobre pagamentos (mandatos)
<!-- prettier-ignore-end -->

## AP2 + A2A para Comunicação Inter-Agente para Pagamentos

O Protocolo de Pagamentos de Agente (AP2) é projetado como uma extensão opcional para protocolos de código aberto como A2A e MCP, permitindo que desenvolvedores construam sobre trabalhos existentes para criar uma estrutura segura e confiável para pagamentos orientados por IA.

- AP2 é necessário para padronizar a comunicação de detalhes de pagamentos como mandatos.
- A2A é necessário para padronizar a comunicação intra-agente, assim que você tiver mais de um agente, você precisa de A2A.

AP2 estende diretamente o protocolo Agent-to-Agent (A2A) para transações de pagamentos multi-agente entre atores como Agentes de Compras, Comerciantes e Provedores de Credenciais.

## AP2 + MCP para Interação com Recursos Externos

MCP é um protocolo que padroniza como modelos de IA e agentes se conectam e interagem com recursos externos como ferramentas, APIs e fontes de dados.

Desenvolvedores podem implementar suas próprias ferramentas para integrar com provedores.

Estamos trabalhando em servidores MCP para AP2.

### Suite MCP E2E 360°

O manifesto [`ap2.e2e360.suite.json`](../../domains/ap2/mcp/manifests/ap2.e2e360.suite.json) consolida os fluxos humano-presente e humano-não-presente, bem como o onboarding de credenciais compatíveis. Ele referencia explicitamente os agentes de Shopping, Merchant, Credentials Provider e Payment Processor, define playbooks MCP (`ap2.e2e.human_present_checkout`, `ap2.e2e.human_absent_checkout`, `ap2.e2e.enable_payment_method`) e aponta as métricas de observabilidade necessárias (`checkout_latency_ms`, `otp_retry_count`). Junto ao manifesto [`pre.e2e360.suite.json`](../../domains/origination-viabilidade/mcp/manifests/pre.e2e360.suite.json), cobrimos 360° do blueprint PRE ↔ AP2 descrito no PRD.

---

Em essência, **A2A e MCP fornecem as camadas fundamentais de comunicação e interação para agentes de IA**, permitindo que eles se conectem e executem tarefas. **AP2 constrói sobre essas camadas adicionando uma extensão de pagamentos especializada e segura**, abordando os desafios únicos de autorização, autenticidade e responsabilidade em pagamentos orientados por IA. Isso permite que agentes naveguem, negociem, comprem e vendam com confiança em nome dos usuários, estabelecendo prova verificável de intenção e responsabilidade clara nas transações.
