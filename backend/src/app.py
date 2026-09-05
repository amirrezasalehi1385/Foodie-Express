from fastapi import FastAPI

from routes.addresses import router as address_router
from routes.auth import router as auth_router
from routes.foods import router as food_router
from routes.menu_item import router as menu_item_router
from routes.menus import router as menu_router
from routes.restaurant_categories import router as restaurant_category_router
from routes.restaurants import router as restaurant_router
from routes.users import router as user_router
from routes.food_categories import router as food_category_router
from routes.favorite_restaurant import router as favorite_router
from routes.cart import router as cart_router
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

app.include_router(
    restaurant_category_router,
    prefix="/api",
)

app.include_router(
    food_router,
    prefix="/api",
)

app.include_router(
    menu_item_router,
    prefix="/api",
)

app.include_router(
    food_category_router,
    prefix="/api"
)


app.include_router(
    favorite_router,
    prefix="/api",
)

app.include_router(
    cart_router,
    prefix="/api",
)