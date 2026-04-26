import os
from dotenv import load_dotenv
from urllib.parse import quote
import json

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth

load_dotenv()

router = APIRouter()

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
    redirect_uri = "http://127.0.0.1:8000/auth"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get("userinfo")

    print("Logged in user:", user)

    user_data = {
    "email": user["email"],
    "name": user.get("name", ""),
    "picture": user.get("picture", "")
}

    encoded = quote(json.dumps(user_data))

    return RedirectResponse(url=f"http://127.0.0.1:8000/?user={encoded}")


# 🔥 You can print or store user here
    print("Logged in user:", user)

# Redirect to frontend (change port if needed)
    return RedirectResponse(url="http://127.0.0.1:8000")
