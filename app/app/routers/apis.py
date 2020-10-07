from fastapi import APIRouter

from app.routers import posts, users

api_router = APIRouter()

api_router.include_router(
    posts.router,
    prefix="/posts",
    tags=["posts"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)
