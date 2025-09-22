# Laboratório de Central de Atendimento com Emulador Android

Este laboratório reúne componentes open source para validar integrações de centrais de atendimento com um emulador Android atua
ndo como softphone. Ele combina Asterisk para sinalização SIP, FreeSWITCH opcional como media server complementar e um serviço C
OTURN para cenários WebRTC. Use-o como base para testes funcionais, de carga leve e para validar fluxos de atendimento assistido
 por agentes digitais.

## Componentes

- **Asterisk 20** – PBX principal com fila de atendimento, ramais SIP de teste e tronco opcional para FreeSWITCH.
- **FreeSWITCH 1.10** (perfil `freeswitch`) – Ligações de vídeo/WebRTC ou integração com aplicações avançadas.
- **coturn** (perfil `webrtc`) – Servidor TURN/STUN para negociação WebRTC quando necessário.

## Pré-requisitos

- Docker 24+ e Docker Compose plugin.
- Host com suporte a virtualização para executar o emulador Android.
- Conectividade de rede entre o host que roda o emulador e o host com Docker.

## Como usar

1. Ajuste as credenciais SIP em `asterisk/conf/pjsip.conf` conforme suas políticas de segurança.
2. (Opcional) Configure parâmetros adicionais de fila em `asterisk/conf/queues.conf`.
3. Inicialize o laboratório:

    ```sh
    cd samples/infra/contact-center-lab
    docker compose up -d asterisk
    ```

4. Para incluir WebRTC com TURN/STUN, habilite o perfil correspondente:

    ```sh
    docker compose --profile webrtc up -d
    ```

5. Para validar cenários híbridos com FreeSWITCH:

    ```sh
    docker compose --profile freeswitch up -d
    ```

6. Configure o softphone dentro do emulador Android com:

    - **Servidor SIP**: endereço IP do host Docker (porta `5060`).
    - **Usuário**: `6001`
    - **Senha**: `androidlab123`
    - **Código de área/Outbound Proxy**: `sip:<ip-do-host>:5060`

7. Adicione um segundo agente SIP (por exemplo, Linphone no desktop) usando o ramal `6002` / senha `qaagent123`.
8. Realize uma chamada discando `6002` ou entre na fila `7000` a partir do softphone do emulador.

## Recursos adicionais

- **Teste de mídia**: disque `7100` para verificar eco/latência.
- **Discagem externa**: prefixe com `9` para enviar a chamada ao tronco FreeSWITCH (`9<destino>`).
- **Logs**: utilize `docker logs contact-center-asterisk -f` para depurar registros de chamadas.
- **Captura de sinalização**: `docker exec -it contact-center-asterisk sngrep`.

## Limpeza

```sh
docker compose down
```

## Próximos passos

- Configurar TLS/WSS para habilitar WebRTC nativo no navegador.
- Integrar gravadores de chamadas (ex.: `asterisk-confbridge` ou `mod_conference`).
- Automatizar testes de regressão com ferramentas como `sipp` ou `sipvicious`.
