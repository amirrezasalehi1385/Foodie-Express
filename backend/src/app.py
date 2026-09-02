from fastapi import FastAPI

from routes.auth import router as auth_router
from routes.user import router as user_router


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(
    auth_router,
    prefix="/api",
)

app.include_router(
    user_router,
    prefix="/api",
)