from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from typing import Optional, Dict, Any

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

async def verify_google_token(token: str) -> Dict[str, Any]:
    try:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), GOOGLE_CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Invalid issuer')

        return {
            "email": idinfo['email'],
            "name": idinfo.get('name'),
            "picture": idinfo.get('picture'),
            "given_name": idinfo.get('given_name'),
            "family_name": idinfo.get('family_name'),
            "locale": idinfo.get('locale'),
            "email_verified": idinfo.get('email_verified', False)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )
