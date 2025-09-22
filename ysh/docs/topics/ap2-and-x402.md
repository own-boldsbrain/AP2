# AP2 e x402

O Protocolo de Pagamentos de Agente (AP2) e [x402](https://www.x402.org/) são complementares. **AP2 é projetado para suportar métodos de pagamento emergentes como x402**, fornecendo uma estrutura segura e interoperável para agentes de IA realizarem transações que podem envolver tais moedas digitais.

<!-- prettier-ignore-start -->
!!! tip "Repositório Dedicado"

    Confira
    [google-agentic-commerce/a2a-x402](https://github.com/google-agentic-commerce/a2a-x402/)
    que é uma implementação de A2A em conjunto com o padrão x402. Nós
    alinharemos isso de perto com AP2 ao longo do tempo para facilitar a composição
    de soluções que incluem todos os métodos de pagamento, incluindo moedas digitais.
<!-- prettier-ignore-end -->

## Agnosticismo de Pagamento e Design à Prova de Futuro

AP2 é um protocolo aberto e interoperável especificamente projetado para permitir que agentes de IA interajam e concluam pagamentos de forma segura e autônoma. Um princípio fundamental do AP2 é seu design agnóstico de método de pagamento e à prova de futuro. A versão inicial suporta métodos de pagamento "pull" comuns como cartões de crédito/débito, com um roteiro para incluir pagamentos "push" como transferências bancárias em tempo real e moedas digitais. Essa abordagem flexível garante que AP2 possa evoluir para suportar várias maneiras como as pessoas pagam.

## Engenharia de Confiança para Transações Agentivas

AP2 introduz conceitos-chave como **Credenciais Verificáveis (VCs)**—incluindo Mandatos de Intenção, Mandatos de Carrinho e Mandatos de Pagamento—que são objetos digitais assinados criptograficamente que capturam a autorização e intenção do usuário. Essas VCs fornecem um rastro de auditoria irrefutável para cada transação, estabelecendo uma estrutura clara para responsabilidade e abordando a "crise de confiança" inerente aos pagamentos autônomos de agentes de IA. Essa base segura é crucial para qualquer método de pagamento onde validar a autoridade do agente e a intenção do usuário é primordial.

## Colaboração da Indústria e Implementação

AP2 está sendo desenvolvido em colaboração com parceiros proeminentes nos ecossistemas de pagamentos e web3, incluindo Coinbase, CrossMint, EigenLayer, Ethereum Foundation, Mesh, Metamask e Mysten. Amostras compartilhadas estão sendo construídas atualmente para demonstrar AP2 e x402 trabalhando juntos em implementações práticas.

---

Em essência, **AP2 fornece o protocolo abrangente seguro e interoperável e mecanismos de confiança necessários para agentes de IA fazerem pagamentos**, enquanto x402 representa um tipo de método de pagamento emergente que AP2 é especificamente projetado para acomodar e suportar de forma segura dentro do ecossistema de pagamentos agentivos.
