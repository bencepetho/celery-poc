import uvicorn
from fastapi import FastAPI

from app.subscription.router import router as subscription_router

app = FastAPI()

app.include_router(subscription_router)


@app.get("/", status_code=204)
async def root():
    return


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
