---
title: Índice de URLs de Referência
---

Este documento contém o índice de URLs e recursos de referência utilizados ao longo do projeto AP2, organizados por categorias.

## Protocolos e Referências

* [A2A Protocol](https://a2a-protocol.org) - Protocolo de comunicação Agent-to-Agent
* [Tema/Epic/Story/Task (Scrum)](https://www.visual-paradigm.com/scrum/theme-epic-user-story-task/) - Guia de referência para metodologia Scrum e Story Mapping

## Repositórios FOSS de Referência (Agentes/Orquestração)

* [Google ADK (docs)](https://github.com/google/adk-docs) - Documentação do Agent Development Kit do Google
* [OpenAI Agents Python (exemplos)](https://github.com/openai/openai-agents-python/tree/main) - Exemplos de implementação de agentes em Python pela OpenAI
* [Rasa – Agentic Orchestration Samples](https://github.com/RasaHQ/agentic-orchestration-samples) - Exemplos de orquestração de agentes utilizando Rasa

## APITable (Exemplos de Endpoints)

Abaixo estão os endpoints utilizados nos exemplos de cURL para integração com APITable:

* Get Records:

    ```http
    https://aitable.ai/fusion/v1/datasheets/{datasheetId}/records
    ```

* Update Records (PATCH):

    ```http
    https://aitable.ai/fusion/v1/datasheets/{datasheetId}/records
    ```

* Add Records (POST):

    ```http
    https://aitable.ai/fusion/v1/datasheets/{datasheetId}/records
    ```

* Delete Records (DELETE):

    ```http
    https://aitable.ai/fusion/v1/datasheets/{datasheetId}/records?recordIds=...
    ```

* Upload Attachments:

    ```http
    https://aitable.ai/fusion/v1/datasheets/{datasheetId}/attachments
    ```

!!! warning "Segurança"
    Substitua `{datasheetId}`, `{viewId}` e tokens por valores do seu ambiente. **Nunca** comita tokens ou credenciais em repositórios.
