from functools import lru_cache

import uvicorn
from fastapi import FastAPI

from app.config import get_settings
from app.subscription.router import router as subscription_router
from app.subscription.worker import get_celery_app


@lru_cache
def get_fastapi_app() -> FastAPI:
    fastapi_api = FastAPI()

    fastapi_api.include_router(subscription_router)

    return fastapi_api


app = get_fastapi_app()
celery = get_celery_app()


@app.get("/", status_code=204)
async def root():
    return


if __name__ == "__main__":
    settings = get_settings()

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=True,
    )
