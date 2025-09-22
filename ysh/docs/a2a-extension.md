# Extensão A2A para AP2

!!! info

    Esta é uma [extensão Agent2Agent (A2A)](https://a2a-protocol.org/latest/topics/extensions/)
    implementando o Protocolo de Pagamentos de Agentes (AP2).

    `v0.1-alpha` (veja [roteiro](roadmap.md))

## URI da Extensão

A URI para esta extensão é
`https://github.com/google-agentic-commerce/ap2/tree/v0.1`.

Agentes que suportam a extensão AP2 DEVEM usar esta URI.

## Função do Agente AP2

Cada Agente que suporta a extensão AP2 DEVE executar pelo menos uma Função da
especificação AP2. Esta função é especificada no
[AgentCard](#objeto-de-extensao-agentcard).

## Objeto de Extensão AgentCard

Agentes que suportam a extensão AP2 DEVEM anunciar seu suporte para uma
extensão AgentCard, usando a [URI da Extensão](#uri-da-extensao).

Os `params` usados no `AgentExtension` DEVEM aderir ao seguinte esquema JSON:

```json
{
  "type": "object",
  "name": "AP2ExtensionParameters",
  "description": "The schema for parameters expressed in AgentExtension.params for the AP2 A2A extension.",
  "properties": {
    "roles": {
      "type": "array",
      "name": "AP2 Roles",
      "description": "The roles that this agent performs in the AP2 model.",
      "minItems": 1,
      "items": {
        "enum": ["merchant", "shopper", "credentials-provider", "payment-processor"]
      }
    }
  },
  "required": ["roles"]
}
```

Este esquema também é expresso pela seguinte definição de tipo Pydantic:

```py
AP2Role = "merchant" | "shopper" | "credentials-provider" | "payment-processor"

class AP2ExtensionParameters(BaseModel):
  # The roles this agent performs in the AP2 model. At least one value is required.
  roles: list[AP2Role] = Field(..., min_length=1)

```

Agentes que executam a função `"merchant"` DEVEM definir a extensão AP2 como
obrigatória. Isso indica que os clientes devem ser capazes de usar a extensão AP2 para
pagar pelos serviços oferecidos pelo agente.

A listagem a seguir mostra um AgentCard declarando suporte à extensão AP2.

```json
{
  "name": "Travel Agent",
  "description": "This agent can book all necessary parts of a vacation",
  "capabilities": {
    "extensions": [
      {
        "uri": "https://github.com/google-agentic-commerce/ap2/tree/v0.1",
        "description": "This agent can pay for reservations on the user's behalf",
        "params": {
          "roles": ["shopper"]
        }
      }
    ]
  },
  "skills": [
    {
      "id": "plan_vacation",
      "name": "Plan Vacation",
      "description": "Plan a fun vacation, creating a full itinerary",
      "tags": []
    },
    {
      "id": "book_itinerary",
      "name": "Book Itinerary",
      "description": "Place reservations for all components of an itinerary (flights, hotels, rentals, restaurants, etc.)",
      "tags": []
    }
  ]
}
```

## Contêineres de Tipos de Dados AP2

As seções a seguir descrevem como os tipos de dados AP2 são encapsulados em tipos de dados A2A.

### Mensagem IntentMandate

Para fornecer um `IntentMandate`, o agente DEVE criar uma Mensagem IntentMandate.
Uma Mensagem IntentMandate é um perfil de `Message` A2A com os seguintes
requisitos.

A Mensagem DEVE conter uma DataPart que contém uma chave de
`ap2.mandates.IntentMandate` e um valor que adere ao esquema `IntentMandate`.

A Mensagem PODE conter uma DataPart que contém uma chave de `risk_data`, onde o
valor contém sinais de risco definidos pela implementação.

A listagem a seguir mostra a renderização JSON de uma Mensagem IntentMandate.

```json
{
  "messageId": "e0b84c60-3f5f-4234-adc6-91f2b73b19e5",
  "contextId": "sample-payment-context",
  "taskId": "sample-payment-task",
  "role": "user",
  "parts": [
    {
      "kind": "data",
      "data": {
        "ap2.mandates.IntentMandate": {
          "user_cart_confirmation_required": false,
          "natural_language_description": "I'd like some cool red shoes in my size",
          "merchants": null,
          "skus": null,
          "required_refundability": true,
          "intent_expiry": "2025-09-16T15:00:00Z"
        }
      }
    }
  ]
}
```

### Artefato CartMandate

Para iniciar uma solicitação de pagamento, um Agente Comerciante DEVE produzir um Artefato CartMandate.
O Artefato CartMandate é um perfil de um Artefato A2A. Um Agente Comerciante
NÃO DEVE produzir um CartMandate até que todas as informações impactantes no pagamento
tenham sido coletadas. Informações impactantes no pagamento são quaisquer informações
fornecidas por um cliente que alteram o CartContents, e portanto o preço a
ser pago. Por exemplo, um endereço de entrega pode alterar o preço do frete que
está incluído no CartContents.

O Artefato CartMandate DEVE ter uma DataPart que contém uma chave de
`ap2.mandates.CartMandate` com um objeto correspondente que adere ao esquema
CartMandate.

O Artefato CartMandate PODE incluir uma DataPart que contém uma chave de
`risk_data` e um valor que contém dados de sinal de risco definidos pela implementação.

A listagem a seguir mostra a representação JSON de um Artefato CartMandate.

```json
{
  "name": "Fancy Cart Details",
  "artifactId": "artifact_001",
  "parts": [
    {
      "kind": "data",
      "data": {
        "ap2.mandates.CartMandate": {
          "contents": {
            "id": "cart_shoes_123",
            "user_signature_required": false,
            "payment_request": {
              "method_data": [
                {
                  "supported_methods": "CARD",
                  "data": {
                    "payment_processor_url": "http://example.com/pay"
                  }
                }
              ],
              "details": {
                "id": "order_shoes_123",
                "displayItems": [
                  {
                    "label": "Cool Shoes Max",
                    "amount": {
                      "currency": "USD",
                      "value": 120.0
                    },
                    "pending": null
                  }
                ],
                "shipping_options": null,
                "modifiers": null,
                "total": {
                  "label": "Total",
                  "amount": {
                    "currency": "USD",
                    "value": 120.0
                  },
                  "pending": null
                }
              },
              "options": {
                "requestPayerName": false,
                "requestPayerEmail": false,
                "requestPayerPhone": false,
                "requestShipping": true,
                "shippingType": null
              }
            }
          },
          "merchant_signature": "sig_merchant_shoes_abc1",
          "timestamp": "2025-08-26T19:36:36.377022Z"
        }
      }
    },
    {
      "kind": "data",
      "data": {
        "risk_data": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...fake_risk_data"
      }
    }
  ]
}
```

### Mensagem PaymentMandate

Para fornecer um PaymentMandate a um agente, o cliente DEVE construir uma
Mensagem PaymentMandate. Uma Mensagem PaymentMandate é um perfil de uma Mensagem A2A.

Uma Mensagem PaymentMandate DEVE conter uma DataPart que tem uma chave de
`ap2.mandates.PaymentMandate` e o valor DEVE ser um objeto que adere ao
esquema `PaymentMandate`.

Uma Mensagem PaymentMandate PODE conter outras Partes.

A listagem a seguir mostra uma renderização JSON de uma Mensagem PaymentMandate.

```json
{
  "messageId": "b5951b1a-8d5b-4ad3-a06f-92bf74e76589",
  "contextId": "sample-payment-context",
  "taskId": "sample-payment-task",
  "role": "user",
  "parts": [
    {
      "kind": "data",
      "data": {
        "ap2.mandates.PaymentMandate": {
          "payment_details": {
            "cart_mandate": "<user-signed hash of the cart mandate>",
            "payment_request_id": "order_shoes_123",
            "merchant_agent_card": {
              "name": "MerchantAgent"
            },
            "payment_method": {
              "supported_methods": "CARD",
              "data": {
                "token": "xyz789"
              }
            },
            "amount": {
              "currency": "USD",
              "value": 120.0
            },
            "risk_info": {
              "device_imei": "abc123"
            },
            "display_info": "<image bytes>"
          },
          "creation_time": "2025-08-26T19:36:36.377022Z"
        }
      }
    }
  ]
}
```
