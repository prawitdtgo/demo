from typing import Optional

from fastapi import APIRouter, Path, Query
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import EmailStr

from app.models.user import UserList, UserData, UserCreation, UserResponse, UserUpdate
from app.mongo import Mongo
from app.responses import get_responses

router = APIRouter()
COLLECTION: AsyncIOMotorCollection = NotImplemented


@router.on_event("startup")
async def start_up() -> None:
    """Execute this function before execute any functions.
    """
    global COLLECTION
    COLLECTION = Mongo.get_collection("user")


@router.get(
    "",
    summary="Get users sorting by updated time in descending order.",
    description="You can search users by email, first name, or last name with regular expression.",
    response_model=UserList,
)
async def get_users(
        request: Request,
        page: int = Query(1, description="Page", ge=1),
        records_per_page: int = Query(10, description="Records per page", ge=1),
        query: Optional[str] = Query(None, description="Search by email, first name, or last name")
) -> dict:
    filters = Mongo.get_regex_filters(query, {"email", "first_name", "last_name"})
    return await Mongo.list(COLLECTION, UserResponse, request, page, records_per_page, filters)


@router.post(
    "",
    summary="Create a user.",
    response_model=UserData,
    status_code=status.HTTP_201_CREATED
)
async def create_user(user_information: UserCreation, request: Request) -> JSONResponse:
    return await Mongo.create(COLLECTION, user_information, UserResponse, request)


@router.get(
    "/{email}",
    summary="Get a user by email.",
    response_model=UserData,
    responses=get_responses({status.HTTP_404_NOT_FOUND})
)
async def get_user(
        email: EmailStr = Path(..., description="Email", example="user@example.com")
) -> JSONResponse:
    return await Mongo.get(COLLECTION, "email", email, UserResponse)


@router.patch(
    "/{email}",
    summary="Update a user by email.",
    response_model=UserData,
    responses=get_responses({status.HTTP_404_NOT_FOUND})
)
async def update_user(
        *,
        email: EmailStr = Path(..., description="Email", example="user@example.com"),
        user_information: UserUpdate
) -> JSONResponse:
    return await Mongo.update(COLLECTION, "email", email, user_information, UserResponse)


@router.delete(
    "/{email}",
    summary="Delete a user by email.",
    responses=get_responses({status.HTTP_404_NOT_FOUND}),
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
        email: EmailStr = Path(..., description="Email", example="user@example.com")
) -> JSONResponse:
    return await Mongo.delete(COLLECTION, "email", email)
