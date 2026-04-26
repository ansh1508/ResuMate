import os
import json
from urllib.parse import quote

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from auth import router as auth_router
from routers.analyzer import router as analyzer_router

# Load environment variables

load_dotenv()

# Create FastAPI app

app = FastAPI(title="ResuMate", version="2.0.0")

# Include routers

app.include_router(auth_router)
app.include_router(analyzer_router, prefix="/api")

# Session middleware (required for OAuth)

app.add_middleware(
SessionMiddleware,
secret_key=os.getenv("SESSION_SECRET", "change-me-in-production")
)

# CORS

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_methods=["*"],
allow_headers=["*"],
)

# OAuth setup

# oauth = OAuth()

# oauth.register(
# name='google',
# client_id=os.getenv("GOOGLE_CLIENT_ID"),
# client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
# server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
# client_kwargs={'scope': 'openid email profile'}
# )

# Login route

# @app.get("/login")
# async def login(request: Request):
#     redirect_uri = request.url_for('auth_callback')
#     return await oauth.google.authorize_redirect(request, redirect_uri)

# # Callback route (IMPORTANT: must match Google Console)

# @app.get("/auth/callback")
# async def auth_callback(request: Request):
#     try:
#         token = await oauth.google.authorize_access_token(request)
#         user = token.get('userinfo')


#         user_data = {
#             "email": user["email"],
#             "name": user.get("name", ""),
#             "picture": user.get("picture", "")
#     }

#     # Send user data to frontend
#         encoded = quote(json.dumps(user_data))
#         return RedirectResponse(url=f"/?user={encoded}")

#     except Exception:
#         return RedirectResponse(url="/?login_error=1")


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
