"""Webhook notification system for pipeline events."""

import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import requests

logger = logging.getLogger("super_dev.webhooks")


def get_webhook_config() -> dict[str, Any]:
    """Load webhook config from env vars."""
    config: dict[str, Any] = {}
    # From env vars (primary)
    url = os.environ.get("SUPER_DEV_WEBHOOK_URL", "")
    if url:
        config["url"] = url
        config["secret"] = os.environ.get("SUPER_DEV_WEBHOOK_SECRET", "")
        config["events"] = os.environ.get(
            "SUPER_DEV_WEBHOOK_EVENTS", "quality_fail,pipeline_complete,overseer_halt"
        ).split(",")
        config["enabled"] = True
    return config


def send_webhook(event_type: str, payload: dict[str, Any]) -> bool:
    """Send a webhook notification."""
    config = get_webhook_config()
    if not config.get("enabled") or not config.get("url"):
        return False

    if event_type not in config.get("events", []):
        return False

    body = {
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }

    headers = {"Content-Type": "application/json"}
    if config.get("secret"):
        signature = hmac.new(
            config["secret"].encode(), json.dumps(body).encode(), hashlib.sha256
        ).hexdigest()
        headers["X-Super-Dev-Signature"] = f"sha256={signature}"

    try:
        resp = requests.post(config["url"], json=body, headers=headers, timeout=10)
        logger.info("Webhook %s sent: %s", event_type, resp.status_code)
        return resp.status_code < 400
    except Exception as e:
        logger.warning("Webhook delivery failed: %s", e)
        return False
