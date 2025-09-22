# Placeholder for aneel_kpis main.py
from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def read_root():
    return {'Hello': 'ANEEL KPIs Service'}
