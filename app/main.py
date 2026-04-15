from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.api.routes.query import router as query_router

app = FastAPI(
    title="AI Research Assistant API",
    version="0.1.0"
)

app.include_router(health_router)
app.include_router(query_router)