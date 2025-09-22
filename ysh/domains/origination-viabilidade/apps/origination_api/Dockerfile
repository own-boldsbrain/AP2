FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY app app
COPY configs configs

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--workers","1","--loop","uvloop"]
