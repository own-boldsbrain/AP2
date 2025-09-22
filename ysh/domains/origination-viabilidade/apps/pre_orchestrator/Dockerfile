FROM python:3.11-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código-fonte
COPY ./pkg/pre_orchestrator /app/pre_orchestrator

# Expor porta
EXPOSE 8000

# Variáveis de ambiente
ENV PYTHONPATH=/app
ENV ORIGINATION_API_URL=http://origination_api:8000
ENV VIABILITY_SERVICE_URL=http://viability_service:8010
ENV ANEEL_TARIFFS_URL=http://aneel_tariffs:8011
ENV ANEEL_KPIS_URL=http://aneel_kpis:8012
ENV ANEEL_UTILITIES_URL=http://aneel_utilities:8013
ENV NATS_URL=nats://nats:4222

# Executar servidor
CMD ["uvicorn", "pre_orchestrator.server:app", "--host", "0.0.0.0", "--port", "8000"]
