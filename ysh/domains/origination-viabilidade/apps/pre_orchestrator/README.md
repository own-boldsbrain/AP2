# PRE Orchestrator Agent

> **Produto**: Yello Solar Hub (YSH) · **Domínio**: `origination-viabilidade`  
> **Missão**: Orquestrar PRE (captação → viabilidade → proposta) com máxima acurácia técnica, regulatória e econômica, gerando 3 ofertas (Base/Plus/Pro), prontos para homologação digital e handoff às próximas fases.

## Visão Geral

O agente orquestrador PRE é responsável por coordenar todo o fluxo desde a captação do lead até a geração de propostas para sistemas solares. Ele interage com diversos serviços via APIs REST e mensageria NATS para realizar análises de viabilidade técnica e econômica, dimensionamento de sistemas, e geração de recomendações personalizadas.

## Funcionalidades Principais

1. **Captação e Validação de Leads**: Garante conformidade com LGPD e integridade dos dados.
2. **Classificação de Consumidores**: Identifica grupo tarifário, classe e subclasse do consumidor.
3. **Seleção de Modalidade**: Determina a modalidade de geração mais adequada (AUTO_LOCAL, AUTO_REMOTO, COMPARTILHADA, MUC).
4. **Análise de Viabilidade**: Calcula a viabilidade técnica do sistema solar com base em dados geográficos e meteorológicos.
5. **Avaliação Econômica**: Determina ROI, payback e TIR para o investimento.
6. **Dimensionamento**: Calcula o tamanho ideal do sistema (kWp) e mapeia para bands e tiers.
7. **Recomendações**: Gera ofertas Base/Plus/Pro com oportunidades de upsell/cross-sell.
8. **Emissão de Eventos**: Publica eventos padronizados no sistema NATS para integração com outros serviços.

## Estrutura do Projeto

- `mcp/manifests/pre_orchestrator_agent.json`: Manifesto do agente MCP com definição de skills.
- `pkg/pre_orchestrator/agent.py`: Implementação principal do agente e suas funcionalidades.
- `pkg/pre_orchestrator/server.py`: Servidor FastAPI para expor as skills do agente via MCP.
- `apps/pre_orchestrator/Dockerfile`: Configuração Docker para implantação.
- `apps/pre_orchestrator/docker-compose.yml`: Configuração para execução do stack completo.

## Uso

### Iniciar o servidor

```bash
cd ysh/domains/origination-viabilidade/apps/pre_orchestrator
docker-compose up -d
```

### Exemplos de chamadas MCP

#### Criar/Atualizar Lead

```json
{
  "skill": {
    "id": "create_update_lead",
    "parameters": {
      "lead_id": "550e8400-e29b-41d4-a716-446655440000",
      "source": "landing",
      "name": "João Silva",
      "email": "joao.silva@example.com",
      "phone": "21999999999",
      "consent": true,
      "cep": "22000-000",
      "uf": "RJ",
      "municipio": "Rio de Janeiro",
      "lat": -22.9,
      "lon": -43.2
    }
  }
}
```

#### Orquestrar Processo PRE Completo

```json
{
  "skill": {
    "id": "orchestrate_pre_process",
    "parameters": {
      "lead_data": {
        "lead_id": "550e8400-e29b-41d4-a716-446655440000",
        "source": "landing",
        "name": "João Silva",
        "email": "joao.silva@example.com",
        "phone": "21999999999",
        "consent": true,
        "cep": "22000-000",
        "uf": "RJ",
        "municipio": "Rio de Janeiro",
        "lat": -22.9,
        "lon": -43.2
      },
      "consumption_data": {
        "consumo_12m_kwh": 4000
      },
      "preferences": {
        "preferred_tier": "T130",
        "has_roof": true,
        "multiple_ucs": false,
        "tilt_deg": 20,
        "azimuth_deg": 180
      },
      "tariff_group": "B1",
      "consumer_class": "RESIDENCIAL",
      "uc_type": "RESIDENCIAL"
    }
  }
}
```

## Formato de Saída

O agente produz um JSON final consolidado conforme o exemplo abaixo:

```json
{
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "inputs_digest": "sha256-placeholder",
  "final_bundle": {
    "lead_id": "550e8400-e29b-41d4-a716-446655440000",
    "classification": {
      "tariff_group": "B1",
      "consumer_class": "RESIDENCIAL",
      "consumer_subclass": "",
      "uc_type": "RESIDENCIAL",
      "generation_modality": "AUTO_LOCAL"
    },
    "viability": {
      "kwh_year_per_kwp": 1121.0,
      "pr": 0.688,
      "mc_result": {}
    },
    "economics": {
      "roi_pct": 23.4,
      "payback_years": 5.8,
      "tir_pct": 18.7
    },
    "sizing": {
      "tier_code": "T130",
      "band_code": "M",
      "kwp": 7.45,
      "expected_kwh_year": 8350
    },
    "offers": [
      {
        "sku":"M-BASE",
        "title":"Kit M Base",
        "capex_estimate": 52150,
        "payback_estimate": 6.0,
        "upsell": ["BATERIA_STD", "DSM_TOU"]
      },
      {
        "sku":"M-PLUS",
        "title":"Kit M Plus",
        "capex_estimate": 59600,
        "payback_estimate": 5.5,
        "upsell": ["BATERIA_STD", "INSURANCE_STD", "O&M_STD"]
      },
      {
        "sku":"M-PRO",
        "title":"Kit M Pro",
        "capex_estimate": 67050,
        "payback_estimate": 5.0,
        "upsell": ["BATERIA_PRO", "INSURANCE_STD", "O&M_STD"]
      }
    ],
    "events_emitted": [
      "lead.captured.v1",
      "generation.modality.selected.v1",
      "viability.requested.v1",
      "viability.completed.v1",
      "system.sized.v1",
      "recommendation.bundle.created.v1"
    ],
    "next_steps": [
      "gerar_proposta_pdf",
      "abrir_tarefa_homologacao",
      "notificar_cliente"
    ]
  },
  "telemetry": {
    "durations_ms": {
      "capture": 123.45,
      "viability": 456.78,
      "tariffs": 78.90,
      "economics": 234.56,
      "sizing_reco": 123.45,
      "total": 1234.56
    },
    "retries": {
      "http": 0,
      "events": 0
    }
  },
  "logs": [
    {"level":"INFO","at":"2025-09-21T10:15:30.123Z","msg":"lead.created"},
    {"level":"INFO","at":"2025-09-21T10:15:31.234Z","msg":"viability.ok"},
    {"level":"INFO","at":"2025-09-21T10:15:32.345Z","msg":"economics.ok"},
    {"level":"INFO","at":"2025-09-21T10:15:33.456Z","msg":"bundle.created"}
  ],
  "errors": []
}
```

## Regras de Negócio

### Dimensionamento

- **Fórmula base**:
  - `Geração_anual = kWp * HSP * 365 * PR * (1 - perdas)`
  - `kWp = (Consumo_anual * fator_tier) / (HSP * 365 * PR * (1 - perdas))`
- **Tiers**: `T115=1.15`, `T130=1.30`, `T145=1.45`, `T160=1.60`.
- **Bands**: `XPP[0–0.5)`, `XS[0.5–3)`, `S[3–6)`, `M[6–12)`, `L[12–30)`, `XL[30–75)`, `XG[75–300)`, `XGG[300–1500)`.

### Modalidades SCEE

- `AUTO_LOCAL` (mesma UC), `AUTO_REMOTO` (UC distinta), `COMPARTILHADA` (geração compartilhada), `MUC` (condomínios).
- Escolha guiada por `uc_type`, `condições do site` e `estratégia fiscal/regulatória`.

### Upsell/Cross-sell

- Bands **XS/S** + perfil **R-N** → `BATERIA_LIGHT`,`INSURANCE_BASIC`,`O&M_BASIC`.
- **M/L** → `BATERIA_STD`,`DSM_TOU`,`INSURANCE_STD`,`O&M_STD`.
- **XL/XG/XGG** → `O&M_PRO`,`INSURANCE_PREMIUM`,`MONITORING_ADVANCED`.
- Modalidade **COMPARTILHADA/MUC** → `RATEIO_AUTOMATION`,`DASHBOARD_PARTICIPANTES`.

## Conformidade

- **LGPD**: Consentimento obrigatório, tratamento adequado de dados pessoais.
- **Auditoria**: Todas as ações são registradas para rastreabilidade.
- **Erros**: Política de retentativas com backoff exponencial.