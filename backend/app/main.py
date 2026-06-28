from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, categories, goals, plans

app = FastAPI(title="PATH API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1 = "/api/v1"
app.include_router(auth.router, prefix=api_v1)
app.include_router(categories.router, prefix=api_v1)
app.include_router(plans.router, prefix=api_v1)
app.include_router(goals.router, prefix=api_v1)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
