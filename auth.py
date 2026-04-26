import os
import json
from urllib.parse import quote

from dotenv import load_dotenv
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth

load_dotenv()

router = APIRouter()

# Read base URL from environment — set this in Render's environment variables
# e.g. RENDER_URL = https://ai-resume-analyzer.onrender.com
BASE_URL = os.getenv("RENDER_URL", "http://127.0.0.1:8000")

oauth = OAuth()

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    },
)


@router.get("/login")
async def login(request: Request):
    redirect_uri = f"{BASE_URL}/auth"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get("userinfo")

        user_data = {
            "email": user["email"],
            "name": user.get("name", ""),
            "picture": user.get("picture", "")
        }

        encoded = quote(json.dumps(user_data))
        return RedirectResponse(url=f"{BASE_URL}/?user={encoded}")

    except Exception:
        return RedirectResponse(url=f"{BASE_URL}/?login_error=1")
