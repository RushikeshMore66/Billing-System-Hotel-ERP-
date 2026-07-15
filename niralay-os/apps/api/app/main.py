# Minimal FastAPI initialization
from fastapi import FastAPI

app = FastAPI(title="NiralayOS API")

@app.get("/")
def read_root():
    return {"message": "NiralayOS API"}
