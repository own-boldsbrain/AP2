# Geo Solar API

Serviço FastAPI que calcula posição solar (azimute/elevação) usando a biblioteca `solposx`.

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Para desenvolvimento com HTTPS forneça `--ssl-keyfile` e `--ssl-certfile`.

## Endpoints

- `GET /healthz`
- `GET /solpos?lat=...&lon=...&iso=...`
