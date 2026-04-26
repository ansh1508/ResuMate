import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from auth import router as auth_router
from routers.analyzer import router as analyzer_router

load_dotenv()

app = FastAPI(title="ResuMate", version="2.0.0")

# ✅ Middleware must be added BEFORE routers
# ✅ SessionMiddleware must come FIRST — OAuth depends on it
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "change-me-in-production")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(analyzer_router, prefix="/api")

# Static files
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/js", StaticFiles(directory="js"), name="js")

# Home route
@app.get("/")
async def home():
    return FileResponse("index.html")

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "project": "ResuMate"}
