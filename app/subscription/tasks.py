import asyncio
import datetime
import json
import time

import httpx
from pydantic import HttpUrl

from app.config import get_app_logger
from app.subscription.exceptions import WebhookError
from app.subscription.schemas import Subscription


async def _is_webhook_reachable(url: str) -> tuple[bool, Exception | None]:
    logger = get_app_logger()

    try:
        async with httpx.AsyncClient() as client:
            await client.head(url)

        logger.info(f"The webhook at {url} is reachable")

    except Exception as exc:
        logger.info(
            f"An error occurred when trying to reach webhook with "
            f"HEAD request at {url}: {exc}"
        )
        return False, exc

    else:
        return True, None


async def send_to_webhook(subscription_name: str, url: HttpUrl) -> httpx.Response:
    logger = get_app_logger()

    async with httpx.AsyncClient() as client:
        data = {
            "subscription_name": subscription_name,
            "time": datetime.datetime.now(datetime.UTC).isoformat(),
        }
        logger.debug(f"Sending data to webhook {url}: {json.dumps(data)}")
        return await client.post(url, json=data)


async def push_messages(
    subscription_name: str,
    payload: Subscription,
):
    logger = get_app_logger()

    reachable, error = await _is_webhook_reachable(payload.webhook_url)

    if not reachable:
        raise WebhookError(
            f"The webhook at {payload.webhook_url} is not reachable"
        ) from error

    started_at = time.time()

    while payload.duration.total_seconds() - (time.time() - started_at) > 0:
        response = await send_to_webhook(subscription_name, payload.webhook_url)

        if response.status_code != payload.expected_status:
            logger.debug(type(response.status_code))
            logger.debug(type(payload.expected_status))
            raise WebhookError(
                f"Webhook response status ({response.status_code}) is "
                f"different from expected ({payload.expected_status})"
            )

        await asyncio.sleep(1)
