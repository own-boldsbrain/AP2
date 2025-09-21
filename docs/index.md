---
hide:
    - toc
---

<!-- markdownlint-disable MD041 -->
<div style="text-align: center;">
  <div class="centered-logo-text-group">
    <img src="assets/ap2-logo-black.svg" alt="Logotipo do Protocolo de Pagamentos de Agentes" width="100">
    <h1>Protocolo de Pagamentos de Agentes (AP2)</h1>
  </div>
</div>

## O que é AP2?

**O Protocolo de Pagamentos de Agentes (AP2) é um protocolo aberto para a emergente Economia de Agentes.** Ele é projetado para permitir comércio seguro, confiável e interoperável entre agentes para desenvolvedores, comerciantes e a indústria de pagamentos. O protocolo está disponível como uma extensão do protocolo de código aberto [Agent2Agent (A2A)](https://a2a-protocol.org/), com mais integrações em andamento.

<!-- prettier-ignore-start -->
!!! abstract ""

    Construa agentes com
    **[![Logotipo ADK](https://google.github.io/adk-docs/assets/agent-development-kit.png){class="twemoji lg middle"} ADK](https://google.github.io/adk-docs/)**
    _(ou qualquer framework)_, equipe com
    **[![Logotipo MCP](https://modelcontextprotocol.io/mcp.png){class="twemoji lg middle"} MCP](https://modelcontextprotocol.io)**
    _(ou qualquer ferramenta)_, colabore via
    **[![Logotipo A2A](https://a2a-protocol.org/latest/assets/a2a-logo-black.svg){class="twemoji sm middle"} A2A](https://a2a-protocol.org)**, e use
    **![Logotipo AP2](./assets/ap2-logo-black.svg){class="twemoji sm middle"} AP2** para proteger pagamentos com agentes de IA generativa.
<!-- prettier-ignore-end -->

<div class="grid cards" markdown>

- :material-play-circle:{ .lg .middle } **Vídeo** Introdução em <7 min

    ---

      <iframe width="560" height="315" src="https://www.youtube.com/embed/yLTp3ic2j5c?si=kfASyAVW8QpzUTho" title="Player de vídeo do YouTube" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

- :material-file-document-outline:{ .lg .middle } **Leia a documentação**

    ---

    [:octicons-arrow-right-24: Anúncio do Google Cloud sobre AP2](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol)

    Explore a definição técnica detalhada do protocolo AP2

    [:octicons-arrow-right-24: Especificação do Protocolo de Pagamentos de Agentes](./specification.md)

    Revise tópicos principais

    [:octicons-arrow-right-24: Visão Geral](topics/what-is-ap2.md)<br>
    [:octicons-arrow-right-24: Conceitos Principais](topics/core-concepts.md)<br>
    [:octicons-arrow-right-24: AP2, A2A e MCP](topics/ap2-a2a-and-mcp.md)<br>
    [:octicons-arrow-right-24: AP2 e x402](topics/ap2-and-x402.md)<br>
    [:octicons-arrow-right-24: Privacidade e Segurança](topics/privacy-and-security.md)<br>

</div>

---

## Por que um Protocolo de Pagamentos de Agentes é Necessário

Os sistemas de pagamento atuais assumem que um humano está clicando diretamente em "comprar" em um site confiável. Quando um agente autônomo inicia um pagamento, essa suposição fundamental é quebrada, levando a questões críticas que os sistemas atuais não podem responder:

- **Autorização:** Como podemos verificar que um usuário deu autoridade específica a um agente para uma compra particular?
- **Autenticidade:** Como um comerciante pode ter certeza de que a solicitação de um agente reflete com precisão a verdadeira intenção do usuário, sem erros ou "alucinações" de IA?
- **Responsabilidade:** Se ocorrer uma transação fraudulenta ou incorreta, quem é responsável—o usuário, o desenvolvedor do agente, o comerciante ou o emissor?

Essa ambiguidade cria uma crise de confiança que poderia limitar significativamente a adoção. Sem um protocolo comum, corremos o risco de um ecossistema fragmentado de soluções de pagamento proprietárias, que seriam confusas para os usuários, caras para os comerciantes e difíceis para as instituições financeiras gerenciarem. O AP2 visa criar uma linguagem comum para qualquer agente compatível transacionar de forma segura com qualquer comerciante compatível globalmente.

---

## Princípios e Objetivos Principais

O Protocolo de Pagamentos de Agentes é construído com base em princípios fundamentais projetados para criar um ecossistema seguro e justo:

- **Abertura e Interoperabilidade:** Como uma extensão não proprietária e aberta para A2A e MCP, o AP2 promove um ambiente competitivo para inovação, alcance amplo de comerciantes e escolha do usuário.
- **Controle e Privacidade do Usuário:** O usuário deve sempre estar no controle. O protocolo é projetado com privacidade em seu núcleo, usando uma arquitetura baseada em papéis para proteger detalhes de pagamento sensíveis e informações pessoais.
- **Intenção Verificável, Não Ação Inferida:** A confiança nos pagamentos é ancorada em prova determinística e irrefutável de intenção do usuário, abordando diretamente o risco de erro ou alucinação do agente.
- **Responsabilidade Clara da Transação:** O AP2 fornece um rastro de auditoria criptográfico irrefutável para cada transação, auxiliando na resolução de disputas e construindo confiança para todos os participantes.
- **Global e Preparado para o Futuro:** Projetado como uma base global, a versão inicial suporta métodos de pagamento comuns de "pull", como cartões de crédito e débito. O roteiro inclui pagamentos de "push", como transferências bancárias em tempo real (por exemplo, UPI e PIX) e moedas digitais.

---

## Conceito Principal: Credenciais Digitais Verificáveis (VDCs)

O Protocolo de Pagamentos de Agentes engenha confiança no sistema usando **credenciais digitais verificáveis (VDCs)**. As VDCs são objetos digitais à prova de adulteração, assinados criptograficamente, que servem como blocos de construção de uma transação. Elas são as cargas de dados que os agentes criam e trocam. Há três tipos principais:

- **O Mandato de Intenção:** Esta VDC captura as condições sob as quais um Agente de IA pode fazer uma compra em nome do usuário, particularmente em cenários "humano-não-presente". Ele fornece ao agente autoridade para executar uma transação dentro de restrições definidas.
- **O Mandato do Carrinho:** Esta VDC captura a autorização final e explícita do usuário para um carrinho específico, incluindo os itens exatos e o preço, em cenários "humano-presente". A assinatura criptográfica do usuário neste mandato fornece prova irrefutável de sua intenção.
- **O Mandato de Pagamento:** Uma VDC separada compartilhada com a rede de pagamento e o emissor, projetada para sinalizar o envolvimento de agente de IA e a presença do usuário (humano-presente ou não) para ajudar a avaliar o contexto da transação.

Essas VDCs operam dentro de uma arquitetura baseada em papéis definida e podem lidar com tipos de transação "humano-presente" e "humano-não-presente".

Saiba mais em [Conceitos Principais](topics/core-concepts.md).

## Veja em ação

<div class="grid cards" markdown>

- **Cartões Humano Presente**

    ---

    Uma amostra demonstrando uma transação humano-presente usando pagamentos tradicionais com cartão.

    [:octicons-arrow-right-24: Ir para amostra](https://github.com/google-agentic-commerce/AP2/tree/main/samples/python/scenarios/a2a/human-present/cards/)

- **x402 Humano Presente**

    ---

    Uma amostra demonstrando uma transação humano-presente usando o protocolo x402 para pagamentos.

    [:octicons-arrow-right-24: Ir para amostra](https://github.com/google-agentic-commerce/AP2/tree/main/samples/python/scenarios/a2a/human-present/x402/)

- **Credenciais de Pagamento Digital Android**

    ---

    Uma amostra demonstrando o uso de credenciais de pagamento digital em um dispositivo Android.

    [:octicons-arrow-right-24: Ir para amostra](https://github.com/google-agentic-commerce/AP2/tree/main/samples/android/scenarios/digital-payment-credentials/run.sh)

</div>

---

## Comece e Construa Conosco

O Protocolo de Pagamentos de Agentes fornece um mecanismo para pagamentos seguros, e faz parte de um quadro maior para desbloquear o pleno potencial do comércio habilitado por agentes. Buscamos ativamente seu feedback e contribuições para ajudar a construir o futuro do comércio.

A especificação técnica completa, documentação e implementações de referência estão hospedadas em nosso repositório público no GitHub.

Você pode começar hoje:

- Baixando e executando nossas **amostras de código**.
- **Experimentando com o protocolo** e seus diferentes papéis de agentes.
- Contribuindo com seu feedback e **código** para o repositório público.

[Visite o Repositório no GitHub](https://github.com/google-agentic-commerce/AP2)
