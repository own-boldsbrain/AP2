# Privacidade e Segurança

O Protocolo de Pagamentos de Agente (AP2) é projetado com privacidade e segurança como pilares fundamentais. Ao reimaginar o fluxo de transações para um mundo nativo de IA, o protocolo introduz novas salvaguardas ao mesmo tempo em que adapta medidas de segurança existentes.

## Princípios Fundamentais

- **Controle do Usuário e Privacidade por Design**: O usuário deve sempre ser a autoridade máxima. O protocolo é arquitetado para dar aos usuários controle granular e visibilidade transparente sobre as atividades financeiras de seus agentes. A privacidade é um princípio fundamental de design, não uma reflexão tardia. O protocolo é projetado para proteger informações sensíveis do usuário, incluindo prompts conversacionais e detalhes pessoais de pagamento.

- **Arquitetura Baseada em Funções**: Um recurso de segurança chave é a separação de preocupações entre os diferentes atores (Agente de Compras, Provedor de Credenciais, Comerciante). Esta arquitetura garante que agentes envolvidos no processo de compra e descoberta sejam impedidos de acessar dados sensíveis da indústria de cartões de pagamento (PCI) ou outras informações pessoalmente identificáveis (PII). Estes dados sensíveis são tratados exclusivamente por entidades especializadas como o Provedor de Credenciais e os elementos seguros da infraestrutura de pagamento existente.

## Um Novo Cenário de Risco

A mudança da interação humana direta para pagamentos agentivos delegados introduz novos fatores de risco que o protocolo é projetado para mitigar ao longo do tempo. Todos os participantes no ecossistema devem reavaliar como estabelecem confiança e gerenciam risco. Considerações-chave incluem:

- **Assincronia do Usuário**: O usuário pode não estar presente durante toda a jornada de pagamento, exigindo mandatos robustos e verificáveis para substituir sua aprovação em tempo real.
- **Confiança Delegada**: Os atores devem agora confiar em um agente para iniciar um pagamento em nome do usuário, tornando a verificação da identidade e autoridade do agente crítica.
- **Estabelecimento de Confiança Indireta**: O Provedor de Credenciais pode não ter um relacionamento direto com o comerciante e deve confiar no Agente de Compras para preencher essa lacuna de confiança de forma segura.
- **Identidade do Agente**: A identidade do Agente de Compras se torna um novo sinal crítico para análise de fraude e risco, exigindo novos métodos de verificação.

O protocolo fornece uma linguagem comum para compartilhar sinais de risco entre entidades, permitindo uma avaliação mais holística e segura de cada transação. Sistemas de risco existentes que comerciantes, redes e emissores têm em vigor podem ser aumentados com novos pontos de dados do fluxo agentivo, como o `PaymentMandate`, garantindo compatibilidade retroativa e aprimorando a segurança.
