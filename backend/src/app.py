from fastapi import FastAPI

from routes.auth import router as auth_router
from routes.users import router as user_router
from routes.restaurants import router as restaurant_router
from routes.addresses import router as address_router
from routes.menus import router as menu_router
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

app.include_router(
    restaurant_router,
    prefix="/api",
)

app.include_router(
    address_router,
    prefix="/api"
)

app.include_router(
    menu_router,
    prefix="/api"
)