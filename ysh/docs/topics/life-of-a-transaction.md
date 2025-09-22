# Vida de uma Transação

O Protocolo de Pagamentos de Agente (AP2) define fluxos claros para diferentes cenários de usuário. As duas modalidades principais são "Humano Presente" e "Humano Não Presente".

## Transação com Humano Presente

Esta jornada se aplica quando um usuário delega uma tarefa a um agente e está disponível para autorizar o pagamento final.

O fluxo típico é o seguinte:

1. **Configuração**: O usuário pode estabelecer uma conexão entre seu Agente de Compras preferido e um Provedor de Credenciais suportado (por exemplo, sua carteira digital).
2. **Descoberta e Negociação**: O usuário dá uma tarefa de compra ao seu agente. O agente interage com um ou mais comerciantes para montar um carrinho que satisfaça a solicitação.
3. **Comerciante Valida Carrinho**: O usuário autoriza um conjunto de itens para compra. O comerciante assina o carrinho final, sinalizando seu compromisso em cumpri-lo.
4. **Fornecer Métodos de Pagamento**: O Agente de Compras solicita um método de pagamento aplicável do Provedor de Credenciais.
5. **Mostrar Carrinho**: O agente apresenta o carrinho final assinado pelo comerciante e o método de pagamento selecionado ao usuário em uma interface confiável.
6. **Assinar e Pagar**: A aprovação do usuário gera um **Mandato do Carrinho** assinado criptograficamente, que contém os detalhes explícitos da compra. Este mandato é compartilhado com o comerciante como evidência. Um **Mandato de Pagamento** separado é preparado para a rede de pagamento.
7. **Execução do Pagamento**: Os detalhes do pagamento são transmitidos ao Provedor de Credenciais e Comerciante para completar a transação.
8. **Enviar ao Emissor**: O comerciante ou seu processador roteia a transação para a rede de pagamento e emissor, anexando o Mandato de Pagamento para fornecer visibilidade na natureza agentiva da transação.
9. **Desafio (Se Necessário)**: Qualquer parte (emissor, comerciante, etc.) pode emitir um desafio (como 3D Secure). O usuário deve completar o desafio em uma superfície confiável.
10. **Autorização**: O emissor aprova o pagamento, e a confirmação é enviada ao usuário e comerciante para que o pedido possa ser cumprido.

## Transação com Humano Não Presente

Esta jornada é para cenários onde o usuário quer que o agente proceda com um pagamento em sua ausência (por exemplo, "compre estes sapatos quando o preço cair abaixo de $100").

As principais diferenças do fluxo com Humano Presente são:

1. **Intenção é Capturada**: Em vez de aprovar um carrinho final, o usuário aprova a _compreensão_ do agente de sua intenção. A autenticação em sessão do usuário (por exemplo, biométrica) cria um **Mandato de Intenção** assinado.
2. **Mandato de Intenção é Usado**: Este mandato, que inclui a descrição em linguagem natural do objetivo do usuário, é compartilhado com o comerciante, que pode então decidir se pode cumprir a solicitação.
3. **Comerciante Pode Forçar Confirmação do Usuário**: Se o comerciante não tiver certeza sobre sua capacidade de cumprir a solicitação com base no Mandato de Intenção, eles podem exigir que o usuário retorne à sessão para confirmar detalhes. Isso pode envolver o usuário selecionando de um conjunto de opções finais (criando um Mandato do Carrinho) ou fornecendo mais informações (atualizando o Mandato de Intenção).

Isso garante que os comerciantes tenham confiança na intenção do usuário, ao mesmo tempo em que permite a execução autônoma de tarefas.
