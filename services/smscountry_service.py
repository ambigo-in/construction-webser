"""
SMSCountry integration (matches the provided reference flow).
"""
from __future__ import annotations

import base64
from functools import lru_cache
from typing import Optional

import httpx
from fastapi import HTTPException, status

from config import settings


class SMSCountryService:
    def __init__(self) -> None:
        if not settings.SMS_COUNTRY_KEY or not settings.SMS_COUNTRY_TOKEN:
            raise RuntimeError("SMSCountry is not configured. Set SMS_COUNTRY_KEY and SMS_COUNTRY_TOKEN.")

        self._key = settings.SMS_COUNTRY_KEY
        self._token = settings.SMS_COUNTRY_TOKEN

    def _auth_header(self) -> str:
        credentials = f"{self._key}:{self._token}"
        encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return f"Basic {encoded}"

    async def send_sms(self, *, number: str, content: str, sender_id: Optional[str] = None) -> None:
        """
        `number` must be 10-digit Indian mobile number (no +91 prefix).
        """
        sender = sender_id or settings.SMS_SENDER_ID
        url = f"https://restapi.smscountry.com/v0.1/Accounts/{self._key}/SMSes/"

        headers = {
            "Authorization": self._auth_header(),
            "Content-Type": "application/json",
        }

        payload = {
            "Number": f"{settings.SMS_DEFAULT_COUNTRY_CODE}{number}",
            "Text": content,
            "SenderId": sender,
        }
        # Some DLT setups require passing a template id. If your account needs this,
        # set SMS_DLT_TEMPLATE_ID in .env.
        if settings.SMS_DLT_TEMPLATE_ID:
            # Field name varies by provider; SMSCountry commonly accepts TemplateId.
            payload["TemplateId"] = settings.SMS_DLT_TEMPLATE_ID

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                if not resp.is_success:
                    # include response body for debugging (usually small)
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"SMSCountry send failed ({resp.status_code}): {resp.text}",
                    )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"SMSCountry error: {e}")


@lru_cache(maxsize=1)
def get_smscountry_service() -> SMSCountryService:
    try:
        return SMSCountryService()
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
