# Conceitos Principais

O Protocolo de Pagamentos de Agente (AP2) é construído sobre uma base de princípios fundamentais e uma arquitetura baseada em funções projetada para criar um ecossistema seguro, interoperável e justo.

## Princípios Orientadores

- **Abertura e Interoperabilidade**: AP2 é uma extensão aberta e não proprietária para protocolos agente-a-agente, promovendo um ambiente competitivo onde qualquer agente compatível pode trabalhar com qualquer comerciante compatível.
- **Controle e Privacidade do Usuário**: O usuário é sempre a autoridade máxima. O protocolo é projetado com privacidade em seu núcleo, usando uma arquitetura baseada em funções e criptografia para proteger dados sensíveis do usuário e detalhes de pagamento.
- **Intenção Verificável, Não Ação Inferida**: A confiança é ancorada em prova determinística e irrefutável de intenção do usuário, abordando diretamente o risco de erro do agente ou "alucinação".
- **Responsabilidade Clara da Transação**: Para que o ecossistema de pagamentos abrace pagamentos agentivos, não pode haver ambiguidade quanto à responsabilidade da transação. O protocolo fornece evidências de suporte que ajudam as redes de pagamento a estabelecer princípios claros e justos para responsabilidade e resolução de disputas. Ao criar um rastro de auditoria criptográfico irrefutável para cada transação, a estrutura fornece as evidências necessárias para resolver disputas com confiança.

## Uma Arquitetura Baseada em Funções

O protocolo define uma clara separação de preocupações atribuindo funções distintas a cada ator no ecossistema:

- **O Usuário**: O indivíduo que delega uma tarefa de pagamentos a um agente.
- **Agente do Usuário (UA) / Agente de Compras (SA)**: A superfície de IA com a qual o usuário interage (por exemplo, Gemini, ChatGPT). Ele entende as necessidades do usuário, constrói um carrinho e obtém a autorização do usuário.
- **Provedor de Credenciais (CP)**: Uma entidade especializada (por exemplo, uma carteira digital) que gerencia com segurança as credenciais e métodos de pagamento do usuário.
- **Ponto Final do Comerciante (ME)**: Uma interface ou agente operando em nome do comerciante para exibir produtos e negociar um carrinho.
- **Ponto Final do Processador de Pagamento do Comerciante (MPP)**: A entidade que constrói a mensagem final de autorização de transação para a rede de pagamento.
- **Rede e Emissor**: A rede de pagamento e a instituição financeira que emitiu as credenciais de pagamento do usuário.

## Âncoras de Confiança: Credenciais Digitais Verificáveis (VDCs)

A inovação central do AP2 é o uso de **credenciais digitais verificáveis (VDCs)** para engenhar confiança. VDCs são objetos digitais à prova de adulteração, portáteis e assinados criptograficamente que servem como blocos de construção de uma transação. Elas são a linguagem de confiança trocada entre agentes.

Existem três tipos principais de VDCs:

### 1. O Mandato do Carrinho (Humano Presente)

O Mandato do Carrinho é a credencial fundamental usada quando o usuário está presente para autorizar uma compra. Ele é gerado pelo Comerciante e assinado criptograficamente pelo usuário (normalmente via seu dispositivo), vinculando sua identidade e autorização a uma transação específica.

Um Mandato do Carrinho contém:

- Identidades verificáveis para o pagador e recebedor.
- Uma representação tokenizada do método de pagamento específico.
- Os detalhes finais e exatos da transação (produtos, destino, valor, moeda).
- Um contêiner para sinais relacionados ao risco.

<div class="grid cards">
    <figure markdown="span" class="card thumb">
        <a href="/assets/GMSCoreDPCScreen-legacy.png">
            <img src="/assets/GMSCoreDPCScreen-legacy.png" alt="Android Digital Payments Credentials Screen"/>
        </a>
        <figcaption>Android Confirmation (current UI)</figcaption>
    </figure>
    <figure markdown="span" class="card thumb">
        <a href="/assets/GMSCoreDPCScreen-future.png">
            <img src="/assets/GMSCoreDPCScreen-future.png" alt="Android Digital Payments Credentials Screen (coming soon)"/>
        </a>
        <figcaption>Android Confirmation (coming soon)</figcaption>
    </figure>
</div>

### 2. O Mandato de Intenção Assinado pelo Usuário (Humano Não Presente)

O Mandato de Intenção Assinado pelo Usuário é usado para cenários onde o usuário não está presente no momento da transação (por exemplo, "compre estes ingressos quando eles forem colocados à venda"). Ele é gerado pelo Agente de Compras e assinado pelo usuário, concedendo ao agente autoridade para agir dentro de restrições definidas.

Um Mandato de Intenção Assinado pelo Usuário contém:

- Identidades verificáveis para o pagador e recebedor.
- Uma lista ou categoria de métodos de pagamento autorizados.
- A intenção de compra, incluindo parâmetros como categorias de produtos e outros critérios.
- A compreensão em linguagem natural do agente do prompt do usuário.
- Um tempo de expiração (Time-to-Live).

### 3. O Mandato de Pagamento

Esta é uma VDC separada compartilhada com a rede de pagamento e emissor. Seu propósito é fornecer visibilidade na natureza agentiva da transação, ajudando a rede e o emissor a construir confiança e avaliar risco. Ela contém sinais para presença de agente de IA e a modalidade da transação (Humano Presente vs. Não Presente).
