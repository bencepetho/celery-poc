import asyncio
import datetime
import json
import time

import httpx
from celery import shared_task
from celery.utils.log import get_task_logger

from app.subscription.exceptions import WebhookError

logger = get_task_logger(__name__)


async def _is_webhook_reachable(url: str) -> tuple[bool, Exception | None]:
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


async def _send_to_webhook(subscription_name: str, url: str) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        data = {
            "subscription_name": subscription_name,
            "time": datetime.datetime.now(datetime.UTC).isoformat(),
        }
        logger.debug(f"Sending data to webhook {url}: {json.dumps(data)}")
        return await client.post(url, json=data)


def sync_async_executor(to_await):
    async_response = []

    async def run_and_capture_result():
        r = await to_await
        async_response.append(r)

    loop = asyncio.get_event_loop()
    coroutine = run_and_capture_result()
    loop.run_until_complete(coroutine)
    return async_response[0]


@shared_task(bind=True, name="subscription.push_messages")
def push_messages(
    self,
    subscription_name: str,
    duration: int,
    webhook_url: str,
    expected_status: int,
):
    reachable, error = sync_async_executor(_is_webhook_reachable(webhook_url))

    logger.info(self)

    if not reachable:
        raise WebhookError(f"The webhook at {webhook_url} is not reachable") from error

    started_at = time.time()

    while duration - (time.time() - started_at) > 0:
        response = sync_async_executor(_send_to_webhook(subscription_name, webhook_url))

        if response.status_code != expected_status:
            logger.debug(type(response.status_code))
            logger.debug(type(expected_status))
            raise WebhookError(
                f"Webhook response status ({response.status_code}) is "
                f"different from expected ({expected_status})"
            )

        sync_async_executor(asyncio.sleep(1))
