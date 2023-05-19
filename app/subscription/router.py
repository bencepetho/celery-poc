import json

from celery.result import AsyncResult
from fastapi import APIRouter
from pydantic import UUID4
from starlette.status import HTTP_200_OK

from app.dependencies import Logger
from app.subscription.schemas import (
    Subscription,
    SubscriptionTask,
    SubscriptionStatus,
)
from app.subscription.tasks import push_messages

router = APIRouter()


@router.post(
    "/subscribe/{subscription_name}",
    status_code=HTTP_200_OK,
    response_model=SubscriptionTask,
)
async def create_subscription(
    request_body: Subscription,
    subscription_name: str,
    logger: Logger,
):
    logger.info(
        f"Creating subscription with name {subscription_name}, "
        f"duration {request_body.duration} at URL {request_body.webhook_url}"
    )

    task: AsyncResult = push_messages.apply_async(
        args=[
            subscription_name,
            request_body.duration.total_seconds(),
            str(request_body.webhook_url),
            request_body.expected_status,
        ],
    )

    return {"task_id": task.id}


@router.get(
    "/subscribe/{subscription_name}/{task_id}",
    status_code=HTTP_200_OK,
    response_model=SubscriptionStatus,
)
def check_subscription(
    subscription_name: str,
    task_id: UUID4,
    logger: Logger,
):
    logger.info(
        f"Checking status of subscription {subscription_name} with task ID {task_id}"
    )

    task: AsyncResult = AsyncResult(str(task_id))

    logger.info(f"Task {task}")
    logger.info(f"Task {task.__dict__}")

    if task.state == "SUCCESS":
        response = {
            "task_status": task.state,
            "task_result": task.result,
            "task_id": task_id,
        }
    elif task.state == "FAILURE":
        logger.warning(type(task.backend))
        logger.warning(task.backend)
        response = json.loads(
            task.backend.get(task.backend.get_key_for_task(task.id)).decode("utf-8")
        )
        logger.warning(response)
        del response["children"]
        del response["traceback"]

    else:
        response = {
            "task_status": task.state,
            "task_result": task.info,
            "task_id": task_id,
        }

    logger.info(f"Response: {response}")

    return response
