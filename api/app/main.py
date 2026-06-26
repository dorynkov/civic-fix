from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.routers import auth_router, board, issues, moderation, petitions, submissions, verification
from app.seed import seed_demo

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Civic Fix API", version="0.1.0")

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(issues.router, prefix="/api/v1")
app.include_router(petitions.router, prefix="/api/v1")
app.include_router(board.router, prefix="/api/v1")
app.include_router(submissions.router, prefix="/api/v1")
app.include_router(moderation.router, prefix="/api/v1")
app.include_router(verification.router, prefix="/api/v1")

app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    seed_demo()


# Eager init for scripts / TestClient without lifespan
Base.metadata.create_all(bind=engine)
try:
    seed_demo()
except Exception:
    pass


@app.get("/health")
def health():
    return {"status": "ok", "city": settings.city_default}
