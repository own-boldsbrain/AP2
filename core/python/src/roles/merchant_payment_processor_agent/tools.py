# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tools for the merchant payment processor agent.

Each agent uses individual tools to handle distinct tasks throughout the
shopping and purchasing process.
"""


import datetime
import logging
import time
from typing import Any

from a2a.server.tasks.task_updater import TaskUpdater
from a2a.types import DataPart
from a2a.types import Part
from a2a.types import Task
from a2a.types import TaskState
from a2a.types import TextPart

from ap2.types.mandate import PAYMENT_MANDATE_DATA_KEY
from ap2.types.mandate import PaymentMandate
from common import artifact_utils
from common import message_utils
from common.a2a_extension_utils import EXTENSION_URI
from common.a2a_message_builder import A2aMessageBuilder
from common.payment_remote_a2a_client import PaymentRemoteA2aClient


async def initiate_payment(
    data_parts: list[dict[str, Any]],
    updater: TaskUpdater,
    current_task: Task | None,
    debug_mode: bool = False,
) -> None:
    """Handles the initiation of a payment.

    This tool processa o início de um pagamento com base em um mandato de pagamento.
    Valida o mandato, verifica credenciais e inicia o fluxo de pagamento apropriado.

    Args:
      data_parts: The data parts from the request, containing a PaymentMandate.
      updater: The TaskUpdater instance for updating the task state.
      current_task: The current task, if it exists (for challenge processing).
      debug_mode: Whether the agent is in debug mode.
    """
    try:
        # Extrair e validar o mandato de pagamento
        payment_mandate_data = message_utils.find_data_part(
            PAYMENT_MANDATE_DATA_KEY, data_parts
        )
        if not payment_mandate_data:
            error_message = _create_text_parts('Missing payment_mandate.')
            await updater.failed(
                message=updater.new_agent_message(parts=error_message)
            )
            return

        # Validar o risk_data (opcional em modo de demonstração)
        risk_data = message_utils.find_data_part('risk_data', data_parts)
        if risk_data and isinstance(risk_data, dict):
            risk_score = risk_data.get(
                'transaction_risk_score', 50
            )  # Default médio se não especificado
            # Se score de risco for muito alto, podemos rejeitar a transação
            if risk_score > 75:  # Apenas um exemplo de limite
                error_message = _create_text_parts(
                    f'Transaction declined due to high risk score: {risk_score}'
                )
                await updater.failed(
                    message=updater.new_agent_message(parts=error_message)
                )
                return

        # Validar e processar o mandato de pagamento
        payment_mandate = PaymentMandate.model_validate(payment_mandate_data)

        # Verificar resposta ao desafio, se existir
        challenge_response = (
            message_utils.find_data_part('challenge_response', data_parts) or ''
        )

        # Processar o mandato de pagamento
        await _handle_payment_mandate(
            payment_mandate,
            challenge_response,
            updater,
            current_task,
            debug_mode,
        )
    except Exception as e:
        error_message = _create_text_parts(
            f'Error initiating payment: {str(e)}'
        )
        await updater.failed(
            message=updater.new_agent_message(parts=error_message)
        )


async def _handle_payment_mandate(
    payment_mandate: PaymentMandate,
    challenge_response: str,
    updater: TaskUpdater,
    current_task: Task | None,
    debug_mode: bool = False,
) -> None:
    """Handles a payment mandate.

    If no task is present, it initiates a transaction challenge. If a task
    requires input, it verifies the challenge response and completes the payment.

    Este método verifica o estado atual do fluxo de pagamento e toma a ação apropriada:
    1. Se for um novo pagamento (sem task), inicia um desafio de segurança
    2. Se estiver aguardando input (challenge response), verifica a resposta e conclui o pagamento
    3. Caso contrário, trata de acordo com o estado atual da tarefa

    Args:
      payment_mandate: The payment mandate containing payment details.
      challenge_response: The response to a transaction challenge, if any.
      updater: The task updater for managing task state.
      current_task: The current task, or None if it's a new payment.
      debug_mode: Whether the agent is in debug mode.
    """
    # Validar o mandato de pagamento
    payment_mandate_contents = payment_mandate.payment_mandate_contents
    payment_details = payment_mandate_contents.payment_details_total

    # Log de informação para debug
    logging.info(
        'Processing payment mandate %s for %s %s',
        payment_mandate_contents.payment_mandate_id,
        payment_details.amount.value,
        payment_details.amount.currency,
    )

    # Verificar autorização do usuário, se presente
    if payment_mandate.user_authorization:
        logging.info('Payment mandate includes user authorization')
        # Em uma implementação real, verificaríamos a assinatura do usuário aqui
        # Simulação: poderíamos pular o desafio para mandatos assinados
        # skip_challenge = True

    # Verificar se é um novo pagamento ou continuação de um existente
    if current_task is None:
        # Novo pagamento - iniciar desafio
        await _raise_challenge(updater)
        return
    elif current_task.status.state == TaskState.input_required:
        # Continuação com resposta ao desafio
        await _check_challenge_response_and_complete_payment(
            payment_mandate,
            challenge_response,
            updater,
            debug_mode,
        )
        return
    else:
        # Estado inesperado
        error_message = _create_text_parts(
            f'Unexpected task state: {current_task.status.state}'
        )
        await updater.failed(
            message=updater.new_agent_message(parts=error_message)
        )


async def _raise_challenge(
    updater: TaskUpdater,
) -> None:
    """Raises a transaction challenge.

    This challenge would normally be raised by the issuer, but we don't
    have an issuer in the demo, so we raise the challenge here. For concreteness,
    we are using an OTP challenge in this sample.

    Em um cenário real, este desafio seria gerado pelo emissor do cartão ou
    instituição financeira. Para demonstração, simulamos um desafio OTP (senha
    de uso único) enviado ao dispositivo do usuário.

    Args:
      updater: The task updater.
    """
    # Criar dados do desafio OTP
    challenge_data = {
        'type': 'otp',
        'display_text': (
            'O emissor do método de pagamento enviou um código de verificação '
            'para o número de telefone registrado. Por favor, informe o código abaixo. '
            'Ele será compartilhado com o emissor para autorizar a transação. '
            '(Dica para demonstração: o código é 123)'
        ),
        'attempt': 1,  # Número da tentativa atual
        'max_attempts': 3,  # Máximo de tentativas permitidas
        'expiry': (
            datetime.datetime.now() + datetime.timedelta(minutes=5)
        ).isoformat(),  # Tempo de expiração do OTP
    }

    # Criar mensagem de desafio para o usuário
    text_part = TextPart(
        text='Por favor, forneça o código de verificação para concluir o pagamento.'
    )
    data_part = DataPart(data={'challenge': challenge_data})

    message = updater.new_agent_message(
        parts=[Part(root=text_part), Part(root=data_part)]
    )

    # Atualizar o estado da tarefa para aguardar input
    await updater.requires_input(message=message)


async def _check_challenge_response_and_complete_payment(
    payment_mandate: PaymentMandate,
    challenge_response: str,
    updater: TaskUpdater,
    debug_mode: bool = False,
) -> None:
    """Checks the challenge response and completes the payment process.

    Checking the challenge response would be done by the issuer, but we don't
    have an issuer in the demo, so we do it here.

    Este método valida a resposta ao desafio (código OTP) e, se válida,
    prossegue com a conclusão do pagamento. Em caso de falha, permite novas
    tentativas até o limite configurado.

    Args:
      payment_mandate: The payment mandate.
      challenge_response: The challenge response.
      updater: The task updater.
      debug_mode: Whether the agent is in debug mode.
    """
    # Obter histórico de tentativas anteriores
    attempt_count = 1
    if current_task := updater.current_task:
        # Verificar mensagens anteriores para determinar quantas tentativas já foram feitas
        for msg in current_task.history:
            for part in msg.parts:
                if hasattr(part.root, 'data') and part.root.data.get(
                    'challenge'
                ):
                    attempt_count = part.root.data.get('challenge', {}).get(
                        'attempt', 1
                    )

        # Incrementar contador de tentativas
        attempt_count += 1

    # Verificar se atingiu o limite máximo de tentativas
    if attempt_count > 3:  # Máximo de 3 tentativas
        error_message = _create_text_parts(
            'Número máximo de tentativas excedido. Por favor, inicie uma nova transação.'
        )
        await updater.failed(
            message=updater.new_agent_message(parts=error_message)
        )
        return

    # Validar a resposta ao desafio
    if _challenge_response_is_valid(challenge_response=challenge_response):
        # Resposta válida - prosseguir com o pagamento
        await _complete_payment(payment_mandate, updater, debug_mode)
        return

    # Resposta inválida - solicitar nova tentativa
    challenge_data = {
        'type': 'otp',
        'display_text': (
            f'Código inválido. Tentativa {attempt_count} de 3. '
            'Por favor, verifique o código enviado para seu telefone e tente novamente. '
            '(Dica para demonstração: o código é 123)'
        ),
        'attempt': attempt_count,
        'max_attempts': 3,
        'expiry': (
            datetime.datetime.now() + datetime.timedelta(minutes=5)
        ).isoformat(),
    }

    text_part = TextPart(
        text='Código de verificação incorreto. Por favor, tente novamente.'
    )
    data_part = DataPart(data={'challenge': challenge_data})

    message = updater.new_agent_message(
        parts=[Part(root=text_part), Part(root=data_part)]
    )

    await updater.requires_input(message=message)


async def _complete_payment(
    payment_mandate: PaymentMandate,
    updater: TaskUpdater,
    debug_mode: bool = False,
) -> None:
    """Completes the payment process.

    Este método finaliza o processo de pagamento após validação bem-sucedida:
    1. Obtém as credenciais de pagamento do provedor de credenciais
    2. Processa o pagamento com o emissor/rede
    3. Retorna o resultado da transação

    Args:
      payment_mandate: The payment mandate.
      updater: The task updater.
      debug_mode: Whether the agent is in debug mode.
    """
    try:
        payment_mandate_id = (
            payment_mandate.payment_mandate_contents.payment_mandate_id
        )
        payment_details = (
            payment_mandate.payment_mandate_contents.payment_details_total
        )

        # Log para diagnóstico
        logging.info(
            'Completing payment for mandate %s with amount %s %s',
            payment_mandate_id,
            payment_details.amount.value,
            payment_details.amount.currency,
        )

        # Obter credenciais de pagamento do provedor de credenciais
        payment_credential = await _request_payment_credential(
            payment_mandate, updater, debug_mode
        )

        if not payment_credential:
            await _fail_task(updater, 'Failed to retrieve payment credentials')
            return

        # Processar o pagamento com o emissor/rede (simulado)
        # Em uma implementação real, aqui chamaríamos APIs de processamento de pagamento
        logging.info(
            'Calling issuer to complete payment for %s with payment credential %s...',
            payment_mandate_id,
            payment_credential,
        )

        # Gerar um ID de transação único para rastreamento
        transaction_id = f'tx_{payment_mandate_id[:8]}_{int(time.time())}'

        # Retornar resultado bem-sucedido
        success_data = {
            'status': 'success',
            'transaction_id': transaction_id,
            'timestamp': datetime.datetime.now().isoformat(),
            'amount': {
                'value': payment_details.amount.value,
                'currency': payment_details.amount.currency,
            },
            'payment_method': payment_mandate.payment_mandate_contents.payment_response.method_name,
        }

        success_message = updater.new_agent_message(
            parts=[
                Part(root=TextPart(text='Pagamento processado com sucesso')),
                Part(root=DataPart(data=success_data)),
            ]
        )

        await updater.complete(message=success_message)

    except Exception as e:
        error_message = _create_text_parts(
            f'Error completing payment: {str(e)}'
        )
        await updater.failed(
            message=updater.new_agent_message(parts=error_message)
        )


def _challenge_response_is_valid(challenge_response: str) -> bool:
    """Validates the challenge response.

    Em um cenário real, este método chamaria o emissor do método de pagamento
    para validar o código OTP. Para fins de demonstração, aceitamos o código fixo "123".

    Args:
      challenge_response: O código OTP fornecido pelo usuário.

    Returns:
      True se o código é válido, False caso contrário.
    """
    # Para demonstração, validamos um código fixo
    # Em um sistema real, validaríamos com o emissor do método de pagamento
    return challenge_response == '123'


async def _request_payment_credential(
    payment_mandate: PaymentMandate,
    updater: TaskUpdater,
    debug_mode: bool = False,
) -> str:
  """Sends a request to the Credentials Provider for payment credentials.

  Args:
    payment_mandate: The PaymentMandate containing payment details.
    updater: The task updater.
    debug_mode: Whether the agent is in debug mode.

  Returns:
    payment_credential: The payment credential details.
  """
  token_object = (
      payment_mandate.payment_mandate_contents.payment_response.details.get(
          "token"
      )
  )
  credentials_provider_url = token_object.get("url")

  credentials_provider = PaymentRemoteA2aClient(
      name="credentials_provider",
      base_url=credentials_provider_url,
      required_extensions={EXTENSION_URI},
  )

  message_builder = (
      A2aMessageBuilder()
      .set_context_id(updater.context_id)
      .add_text("Give me the payment method credentials for the given token.")
      .add_data(PAYMENT_MANDATE_DATA_KEY, payment_mandate.model_dump())
      .add_data("debug_mode", debug_mode)
  )
  task = await credentials_provider.send_a2a_message(message_builder.build())

  if not task.artifacts:
    raise ValueError("Failed to find the payment method data.")
  payment_credential = artifact_utils.get_first_data_part(task.artifacts)

  return payment_credential


def _create_text_parts(*texts: str) -> list[Part]:
  """Helper to create text parts."""
  return [Part(root=TextPart(text=text)) for text in texts]


async def _fail_task(updater: TaskUpdater, error_text: str) -> None:
    """A helper function to fail a task with a given error message.

    Args:
      updater: O TaskUpdater para atualizar o estado da tarefa.
      error_text: A mensagem de erro a ser apresentada.
    """
    error_message = updater.new_agent_message(
        parts=[
            Part(root=TextPart(text=error_text)),
            Part(root=DataPart(data={'error': error_text, 'status': 'failed'})),
        ]
    )
    await updater.failed(message=error_message)
