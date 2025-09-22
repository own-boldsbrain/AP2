# Laboratório Open Source para Centrais de Atendimento com Emulador Android

Este guia descreve como combinar ferramentas open source para montar um ambiente de testes completo que permite validar interaç
ões entre sua central de atendimento e um emulador Android atuando como endpoint telefônico. A proposta reúne os blocos de voz 
 tradicionais (Asterisk e FreeSWITCH), comunicação WebRTC e softphones móveis para que você consiga reproduzir chamadas entrante
s, filas de atendimento, URAs e monitoramento sem depender de dispositivos físicos.

## Arquitetura de Referência

A topologia sugerida inclui quatro pilares:

1. **Plataforma PBX (Asterisk)**: núcleo de sinalização SIP, filas, URA e gravação.
2. **Media server complementar (FreeSWITCH)**: funções avançadas como videoconferência, WebRTC nativo e transcodificação.
3. **Serviço TURN/STUN (coturn)**: suporte a cenários WebRTC, principalmente quando o emulador ou agentes remotos estão atrás d
 e NAT.
4. **Emulador Android + Softphone**: executa Linphone, CSipSimple ou outro softphone SIP/WebRTC para representar um atendente ou 
 cliente.

```mermaid
graph TD
    Asterisk[Asterisk 20<br>Filas, URA, Ramais] -->|SIP / RTP| Android[Emulador Android<br>Softphone (Linphone/CSipSimple)]
    Asterisk -->|Tronco SIP| FreeSWITCH[FreeSWITCH 1.10<br>WebRTC, Vídeo, Transcodificação]
    Android -.->|ICE/TURN| Coturn[coturn<br>STUN/TURN]
    Browser[Navegador WebRTC] -->|WSS + ICE| FreeSWITCH
    Browser -->|WSS + ICE| Asterisk
```

> 💡 **Dica**: o diretório [`samples/infra/contact-center-lab`](https://github.com/google-agentic-commerce/AP2/tree/main/samples/infra/contact-center-lab) contém um `docker-compose.yml` com os serviços descritos aqui, pronto para ser adaptado ao seu ambiente.

## Pré-requisitos

- Docker e Docker Compose plugin instalados.
- Host com recursos suficientes para executar Asterisk e o emulador (mínimo 4 vCPUs e 8 GiB de RAM sugeridos).
- Android Studio ou Genymotion para emulação.
- Acesso administrativo para configurar regras de firewall (porta 5060/UDP, faixa RTP, 3478/UDP para TURN).

## Provisionando a camada de voz

1. **Inicialize o Asterisk**

    ```sh
    cd samples/infra/contact-center-lab
    docker compose up -d asterisk
    ```

    - O arquivo [`asterisk/conf/pjsip.conf`](https://github.com/google-agentic-commerce/AP2/blob/main/samples/infra/contact-center-lab/asterisk/conf/pjsip.conf) cria dois ramais (`6001` e `6002`) e um tronco opcional para FreeSWITCH.
    - [`extensions.conf`](https://github.com/google-agentic-commerce/AP2/blob/main/samples/infra/contact-center-lab/asterisk/conf/extensions.conf) expõe o teste de eco (`7100`), fila principal (`7000`) e encaminhamento externo (`9+destino`).

2. **Habilite o TURN/STUN para WebRTC (opcional)**

    ```sh
    docker compose --profile webrtc up -d
    ```

    - O [`turnserver.conf`](https://github.com/google-agentic-commerce/AP2/blob/main/samples/infra/contact-center-lab/coturn/turnserver.conf) define credenciais estáticas (`lab/labpassword`) que podem ser trocadas por segredos gerados dinamicamente.

3. **Adicione FreeSWITCH quando precisar de recursos complementares**

    ```sh
    docker compose --profile freeswitch up -d
    ```

    - O tronco `freeswitch-trunk` já está definido no Asterisk; basta cadastrar um gateway equivalente no FreeSWITCH (`sofia.conf.x
ml`).
    - Utilize o FreeSWITCH para cenários de videoconferência, gravação em múltiplos formatos ou integração com mod_event_socket.

## Configurando o emulador Android

1. Abra o Android Studio e inicie um dispositivo virtual (Pixel 6+ / Android 14 recomendado).
2. Instale um softphone via Google Play ou sideload (`adb install`):

    - **Linphone** – interface simples, suporte a Opus, ZRTP e push.
    - **CSipSimple** – altamente configurável, ideal para testes avançados de SIP.
    - **Jitsi Meet** – útil quando a central expõe WebRTC.

3. Configure a conta SIP no softphone:

    - **Identidade/Usuário**: `6001`
    - **Senha**: `androidlab123`
    - **Servidor/Proxy**: `sip://<ip-do-host-docker>:5060`
    - **Transporte**: UDP (ou TLS/WSS quando configurado).
    - **TURN (quando aplicável)**: `turn://lab:labpassword@<ip-do-host-docker>:3478`.

4. Ajuste a rede do emulador para `Bridged` (Genymotion) ou `NAT` com regras de encaminhamento (Android Studio) para garantir ac
esso direto ao host Docker.

## Fluxos de teste recomendados

1. **Smoke test de ramal** – do softphone no emulador disque `7100` e valide áudio bidirecional.
2. **Fila de atendimento** – registre um segundo agente SIP (`6002`) em outro dispositivo e ligue para `7000`; monitore a distrib
uição de chamadas e timers de `Queue`.
3. **Roteamento externo** – configure um número de teste no FreeSWITCH e valide a discagem com o prefixo `9`.
4. **WebRTC via navegador** – utilize um cliente WebRTC (ex.: [SIP.js demo](https://sipjs.com/demo/)) apontando para o TURN e tran
sporte WSS do Asterisk/FreeSWITCH para simular um agente em browser.
5. **Testes automatizados** – execute `sipp` ou `sipvicious` contra `contact-center-asterisk` para validar resiliência e consumo 
 de recursos.

## Observabilidade e troubleshooting

- `docker logs contact-center-asterisk -f` – visualiza registro de chamadas e eventos de fila.
- `docker exec -it contact-center-asterisk sngrep` – captura SIP em tempo real dentro do contêiner.
- `asterisk -rx "pjsip show registrations"` – confirma registros do emulador.
- `docker logs contact-center-coturn` – avalia negociações ICE/TURN.
- `docker exec -it contact-center-freeswitch fs_cli` – monitora canais quando o FreeSWITCH estiver habilitado.

## Boas práticas e próximos passos

- Habilite TLS e WSS para proteger credenciais SIP, atualizando certificados no Asterisk (`http.conf`/`pjsip.conf`) e no FreeS
WITCH (`wss-binding`).
- Externalize segredos (SIP/TURN) via variáveis de ambiente ou cofre de segredos antes de integrar ao pipeline CI.
- Utilize ferramentas de infraestrutura como código (Terraform, Ansible) para reproduzir o laboratório em múltiplos ambientes.
- Adicione monitoração (Prometheus, Grafana) com exporters como `asterisk-exporter` ou `mod_prometheus`.
- Planeje testes de carga progressivos e automações de regressão antes de conectar a central de atendimento produtiva.
