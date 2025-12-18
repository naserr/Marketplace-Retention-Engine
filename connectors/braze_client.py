"""Mocked Braze API client used to simulate campaign triggers."""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

import requests


class BrazeClient:
    """Lightweight client that mimics Braze campaign triggering."""

    def __init__(self, base_url: str = "https://rest.iad-01.braze.com", api_key: Optional[str] = None, timeout: int = 5) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "mock-api-key"
        self.timeout = timeout

    def trigger_campaign(self, user_id: int, campaign_id: str, attributes: Dict[str, Any]) -> bool:
        """Simulate enrolling a user into a Braze campaign.

        In production this would issue a POST to `/campaigns/trigger/send` with
        user identifiers and custom attributes. Here we log the intent and
        simulate a small amount of latency.
        """
        endpoint = f"{self.base_url}/campaigns/trigger/send"
        payload = {
            "campaign_id": campaign_id,
            "recipients": [
                {
                    "external_user_id": str(user_id),
                    "attributes": attributes,
                }
            ],
        }

        try:
            time.sleep(0.2)
            logging.info(
                "Simulating POST request to Braze API... User %s added to Campaign %s",
                user_id,
                campaign_id,
            )
            logging.debug("Endpoint: %s | Payload: %s", endpoint, payload)
            return True
        except Exception as exc:  # pragma: no cover - defensive logging
            logging.error("Failed to trigger campaign for user %s: %s", user_id, exc)
            return False
