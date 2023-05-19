import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, validator, UUID4
from starlette.status import HTTP_200_OK


class Subscription(BaseModel):
    duration: datetime.timedelta = Field(
        datetime.timedelta(seconds=20),
        title="Duration",
        description="The duration of the subscription",
    )
    webhook_url: HttpUrl = Field(
        title="Webhook URL",
        description="The URL to the webhook used for the subscription",
    )
    expected_status: int = Field(
        HTTP_200_OK,
        title="Expected Status Code",
        description="The expected response status code on the webhook URL",
    )

    @validator("duration")
    def duration_must_be_less_than_ten_minutes(cls, v: datetime.timedelta):
        if not 0 < v.total_seconds() <= 600:
            raise ValueError(
                f"Duration must be less than 600 seconds, "
                f"but it is {v.total_seconds()} second(s)"
            )

        return v


class SubscriptionTask(BaseModel):
    task_id: UUID4 = Field(
        title="Task ID",
        description="The ID of the created subscription task",
    )


class SubscriptionStatus(SubscriptionTask):
    task_status: str = Field(
        title="Task Status",
        description="The status of the created subscription task",
    )
    task_result: Any = Field(
        title="Task Result",
        description="The result of the created subscription task",
    )
