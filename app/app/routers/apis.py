from fastapi import APIRouter

from app.routers import posts, users, authorization, contacts

api_router = APIRouter()

api_router.include_router(
    router=authorization.router,
    prefix="/oauth2",
    tags=["authorization"]
)

api_router.include_router(
    router=users.router,
    prefix="/users",
    tags=["users"]
)


api_router.include_router(
    router=posts.router,
    prefix="/posts",
    tags=["posts"]
)

api_router.include_router(
    router=contacts.router,
    prefix="/contacts",
    tags=["contacts"]
)
