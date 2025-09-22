# Perguntas Frequentes

1. O que posso fazer com este protocolo hoje?

    - Construímos agentes de exemplo em torno da biblioteca principal AP2 em Python que demonstram uma rica experiência de compras. Lance os agentes e tente comprar seus produtos favoritos! Essas amostras simulam provedores de serviços de pagamento reais para que você possa explorar sem dependências. Especificamente, observe os mandatos enquanto os agentes fazem seu trabalho. Publicaremos mais amostras e SDKs em breve, e adoraríamos ver suas ideias! Você pode usar as amostras de código para criar sua própria implementação de um pagamento ocorrendo entre vários agentes de IA ou estender o protocolo para mostrar novos tipos de cenários de pagamento _(digamos, mostrando um pagamento feito por um método de pagamento diferente ou usando uma maneira diferente de autenticação)_.

1. Posso construir meu próprio agente para qualquer um desses papéis, usando um como modelo?

    - Sim, você pode construir seu próprio agente usando qualquer um dos [papéis](topics/core-concepts.md). Comece a construir com [ADK](https://google.github.io/adk-docs/) e [Agent Builder](https://cloud.google.com/products/agent-builder) do Google Cloud, ou qualquer outra plataforma que você escolher para construir agentes.

1. Posso construir meu próprio agente para participar neste protocolo?

    - Sim, você pode construir um agente para qualquer um dos [papéis](topics/core-concepts.md) definidos. Qualquer agente, em qualquer framework (como LangGraph, AG2 ou CrewAI), ou em qualquer runtime, é capaz de implementar AP2.

1. Posso experimentar isso sem fazer um pagamento real?

    - Você pode considerar configurar isso em seus ambientes internos onde você pode já ter maneiras de invocar métodos de pagamento falsos que não exigem movimento real de dinheiro.

1. Há um servidor MCP ou um SDK pronto para "meu framework de escolha"?

    - Estamos trabalhando em um SDK e um servidor MCP agora, em colaboração com provedores de serviços de pagamento. Volte em breve.

1. Isso funciona com o padrão x402 para pagamentos cripto?

    - Projetamos o AP2 para ser um protocolo agnóstico de pagamento, para que o comércio agentic possa ocorrer de forma segura em todos os tipos de sistemas de pagamento. Ele fornece uma base segura e auditável, seja um agente usando um cartão de crédito ou transacionando com stablecoins. Esse design flexível nos permite estender seus princípios principais a novos ecossistemas, garantindo um padrão consistente de confiança em todos os lugares.

        Como primeiro passo, confira [google-agentic-commerce/a2a-x402](https://github.com/google-agentic-commerce/a2a-x402/) que é uma implementação de A2A em conjunto com o padrão x402. Alinharemos isso de perto com o AP2 ao longo do tempo para facilitar a composição de soluções que incluam todos os métodos de pagamento, incluindo stablecoins.

1. O que são credenciais verificáveis?

    - São objetos de dados padronizados e criptograficamente seguros (como o Mandato do Carrinho e o Mandato de Intenção) que servem como blocos de construção à prova de adulteração, não disputáveis e assinados criptograficamente para uma transação.

1. Como o protocolo garante controle e privacidade do usuário?

    - O protocolo é projetado para garantir que o usuário seja sempre a autoridade máxima e tenha controle granular sobre as atividades de seus agentes. Ele protege informações sensíveis do usuário, como prompts de conversa e detalhes de pagamento pessoais, impedindo que agentes de compras acessem dados PCI ou PII sensíveis por meio de criptografia de carga útil e uma arquitetura baseada em papéis.

1. Como o AP2 aborda a responsabilidade da transação?

    - Um objetivo principal é fornecer evidências de apoio que ajudam as redes de pagamento a estabelecer princípios de responsabilidade e responsabilidade. Em uma disputa, o adjudicador da rede (por exemplo, Rede de Cartões) pode usar o mandato do carrinho assinado pelo usuário e comparar os detalhes do que foi acordado entre o agente e o consumidor com os detalhes na disputa para ajudar a determinar a responsabilidade da transação.

1. O que impede um agente de "alucinar" e fazer uma compra incorreta?

    - O princípio de Intenção Verificável, Não Ação Inferida aborda esse risco. As transações devem ser ancoradas em prova determinística e irrefutável de intenção de todas as partes, como o Mandato do Carrinho ou de Intenção assinado pelo usuário, em vez de depender apenas da interpretação das saídas probabilísticas e ambíguas de um modelo de linguagem.

1. Por que o suporte a cripto e Web3 foi incluído desde o primeiro dia?

    - Apoiar uma ampla gama de tipos de pagamento, incluindo métodos de pagamento digitais, garante que o protocolo seja preparado para o futuro. A colaboração com parceiros como Coinbase, Ethereum Foundation e Metamask valida a flexibilidade do AP2 e preenche a lacuna entre as economias tradicionais e Web3, permitindo casos de uso inovadores como micropagamentos.

1. Como posso me envolver?

    - O AP2 é um projeto de código aberto criado pelo Google, semelhante ao protocolo A2A. Contribuições são bem-vindas no Github como discussões, bugs, solicitações de recursos e PRs. Além disso, temos um [formulário de interesse](https://forms.gle/uNc1e7hVhirmqcMs5) para comunicação privada com o Google. A colaboração está acontecendo agora, com novas amostras, integrações e SDKs sendo desenvolvidas – Github ou o formulário de interesse são as melhores maneiras de se comunicar com a equipe AP2.
