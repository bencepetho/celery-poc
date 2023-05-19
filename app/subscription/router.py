import random

from fastapi import APIRouter
from starlette.status import HTTP_200_OK

from app.dependencies import Logger
from app.subscription.schemas import SubscriptionCreated, Subscription
from app.subscription.tasks import push_messages

router = APIRouter()


@router.post(
    "/subscribe/{subscription_name}",
    status_code=HTTP_200_OK,
    response_model=SubscriptionCreated,
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
    await push_messages(subscription_name, request_body)

    return {"task_id": random.randint(0, 100)}
