# Placeholder for aneel_tariffs main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "ANEEL Tariffs Service"}
