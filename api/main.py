from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API en ligne"}

# Instrumentation Prometheus
Instrumentator().instrument(app).expose(app)
