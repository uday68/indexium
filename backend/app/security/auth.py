import os
from typing import Optional
from fastapi import Header, HTTPException, status

API_KEY = os.getenv("API_KEY", "")


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Validate X-API-Key header if an API_KEY environment variable is configured.
    If no API_KEY is set, requests are allowed (development mode).
    """
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return True
