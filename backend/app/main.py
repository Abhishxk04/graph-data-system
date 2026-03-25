from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# graph API
from app.api.routes import router as graph_router

# chat/query API
from app.api.query import router as query_router

app = FastAPI(
    title="Graph Data System API",
    description="Graph + Chat (LLM SQL) Backend",
    version="1.0"
)

# -----------------------------
# CORS (IMPORTANT for frontend)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# ROUTES
# -----------------------------
app.include_router(graph_router, prefix="/api", tags=["Graph"])
app.include_router(query_router, prefix="/api", tags=["Chat"])

# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/")
def root():
    return {
        "message": "Backend is running 🚀",
        "endpoints": {
            "graph": "/api/graph",
            "chat": "/api/query",
            "docs": "/docs"
        }
    }