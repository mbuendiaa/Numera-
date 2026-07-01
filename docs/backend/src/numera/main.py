from fastapi import FastAPI

from numera.api.routes.health import router as health_router
from numera.api.routes.companies import router as companies_router
from numera.api.routes.cognitive import router as cognitive_router

app = FastAPI(
    title="Numera Core Platform",
    version="0.1.0",
    description="AI-native financial intelligence platform backend.",
)

app.include_router(health_router, tags=["Health"])
app.include_router(companies_router, prefix="/companies", tags=["Companies"])
app.include_router(cognitive_router, prefix="/cognitive", tags=["Cognitive System"])
