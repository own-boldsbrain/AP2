---
title: Sumário Executivo
---

Este documento apresenta um sumário abrangente do que foi desenvolvido e construído no projeto AP2, fornecendo uma visão end-to-end de 360° de todas as suas funcionalidades, fases e componentes.

## Blueprint Operacional 360° (YSH)

Implementamos um **Blueprint Operacional 360°** baseado em múltiplos protocolos e frameworks:

* **A2A** (Agent-to-Agent Protocol)
* **MCP** (Model Context Protocol)
* **ACP** (Agent Control Protocol)
* **FIPA-ACL** (Foundation for Intelligent Physical Agents - Agent Communication Language)

Este blueprint cobre todas as fases do ciclo de vida:

* Pré-venda
* Fechamento
* Execução
* O&M (Operação e Manutenção)

Incluindo eventos/KPIs, Definition of Ready (DoR), Definition of Done (DoD), e **story mapping** completo (Theme → Epic → Story → Task).

## Fase Pré-venda

A fase de pré-venda foi detalhada em todos os seus estágios:

1. **Captura/Investigação**: Coleta inicial de dados e informações do cliente
2. **Detecção/Viabilidade**: Análise da viabilidade do projeto
3. **Análise de Consumo**: Estudo do perfil de consumo energético
4. **Dimensionamento/Simulação**: Cálculo do tamanho do sistema e simulações
5. **Recomendações/Finanças**: Propostas e análise financeira

## Landscape de Agentes

Desenvolvemos um **landscape de agentes** completo, abrangendo todas as etapas do processo (end-to-end) com foco especial na fase de pré-venda. Este landscape inclui:

* **Papéis e responsabilidades** de cada agente
* **Entradas e saídas** esperadas
* **Protocolos de comunicação**
* **Métricas de desempenho**

## Estrutura de Repositórios

Sugerimos uma estrutura de repositórios no GitHub organizada da seguinte forma:

* **Monorepo principal**
* Repositório dedicado "pre-sale only"
* **Módulos de protocolos**:
    * A2A (Agent-to-Agent)
    * MCP (Model Context Protocol)
    * FIPA-ACL (Agent Communication Language)
    * ACP (Agent Control Protocol)
* **Serviços**:
    * Lead
    * Validação
    * Deduplicação
    * Enriquecimento público
    * Machine Learning
* **Workflows e testes**

## Frontend e Integração de Dados

* **Frontend Next.js 15** isolado para:
    * Intake
    * Consentimentos
    * Dashboards
    * Propostas

* **Enriquecimento com dados públicos** de múltiplas fontes:
    * ANEEL/EPE
    * INPE/irradiância
    * BACEN/SGS
    * CVM/CKAN
    * CNPJ

  Com funcionalidades de cache/TTL, upsert versionado e evento `LeadEnriched.Public`.

## Integração APITable

Implementamos integração com APITable (alternativa FOSS-friendly) com exemplos de:

* GET/POST/PATCH/DELETE
* Modelos de payload
* Limites de QPS (Queries Per Second)

## Análise e Correção de Erros

Realizamos RCA (Root Cause Analysis) para o erro `'dict' object can't be awaited`:

* Correção do uso de `await` apenas sobre corotinas/Tasks
* Padronização de conectores para `async`/`sync` com wrappers adequados
