# Placeholder for aneel_utilities main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "ANEEL Utilities Service"}
