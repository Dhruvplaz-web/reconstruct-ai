"""
Reconstruct.ai — Backend Application Entrypoint
FastAPI REST Service with CORS, Pydantic v2 schemas, and W3C PROV-DM provenance models.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.router import router

app = FastAPI(
    title="Reconstruct.ai Core API",
    description="Automated project reconstruction and grounded knowledge handover engine.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Next.js 14 frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "project": "Reconstruct.ai",
        "description": "We Code Coders Hackathon — Round 2 Working MVP Backend",
        "institution": "JSPM RSCOE, Pune",
        "team": "TEAM DOMINATOR",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "synthetic_playground": "/api/ingest/synthetic",
            "orphan_risk": "/api/analyze/orphan-risk",
            "contradictions": "/api/analyze/contradictions",
            "temporal_graph": "/api/analyze/graph",
            "leaver_questions": "/api/review/questions",
            "handover_workspace": "/api/handover/workspace"
        }
    }
