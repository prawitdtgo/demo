import json
from typing import Optional

from fastapi import APIRouter, Path, Query
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorCollection

from app.models.post import PostList, PostData, PostCreation, PostDataResponse, PostOwner, PostUpdate
from app.mongo import Mongo
from app.responses import get_responses
from app.types.object_id import ObjectIdStr

router = APIRouter()
COLLECTION: AsyncIOMotorCollection = NotImplemented


@router.on_event("startup")
async def start_up() -> None:
    """Execute this function before execute any functions.
    """
    global COLLECTION
    COLLECTION = Mongo.get_collection("post")


async def add_owner(data: dict) -> None:
    """Add an owner into the specified post data's relationships.

    :param data: Post data
    """
    data.update({
        "relationships": {
            "owner": await Mongo.get_relationship("user", "email", data.pop("owner"), PostOwner)
        }
    })


async def add_relationships(response: JSONResponse) -> None:
    """Add relationships into the specified response's data.

    :param response: Response
    """
    body: dict = json.loads(response.body)
    data: dict = body["data"]
    await add_owner(data)
    response.body = json.dumps(body).encode()
    response.headers["Content-Length"] = str(len(response.body))


@router.get(
    "",
    summary="Get posts sorting by updated time in descending order.",
    description="You can search posts by message with regular expression.",
    response_model=PostList,
)
async def get_posts(
        request: Request,
        page: int = Query(1, description="Page", ge=1),
        records_per_page: int = Query(10, description="Records per page", ge=1),
        query: Optional[str] = Query(None, description="Search by message")
) -> dict:
    filters = Mongo.get_regex_filters(query, {"message"})
    result: dict = await Mongo.list(COLLECTION, PostDataResponse, request, page, records_per_page, filters)

    for post in result["data"]:
        await add_owner(post)

    return result


@router.post(
    "",
    summary="Create a post.",
    response_model=PostData,
    status_code=status.HTTP_201_CREATED
)
async def create_post(post_information: PostCreation, request: Request) -> JSONResponse:
    response: JSONResponse = await Mongo.create(COLLECTION, post_information, PostDataResponse, request)
    if response.status_code == status.HTTP_201_CREATED:
        await add_relationships(response)
    return response


@router.get(
    "/{post_id}",
    summary="Get a post by post ID.",
    response_model=PostData,
    responses=get_responses({status.HTTP_404_NOT_FOUND})
)
async def get_post(
        post_id: ObjectIdStr = Path(..., description="Post ID", example="5f43825c66f4c0e20cd17dc3")
) -> JSONResponse:
    response = await Mongo.get_by__id(COLLECTION, post_id, PostDataResponse)
    if response.status_code == status.HTTP_200_OK:
        await add_relationships(response)
    return response


@router.put(
    "/{post_id}",
    summary="Update a post by post ID.",
    response_model=PostData,
    responses=get_responses({status.HTTP_404_NOT_FOUND})
)
async def update_post(
        *,
        post_id: str = Path(..., description="Post ID", example="5f43825c66f4c0e20cd17dc3"),
        post_information: PostUpdate
) -> JSONResponse:
    response = await Mongo.update_by__id(COLLECTION, post_id, post_information, PostDataResponse)
    if response.status_code == status.HTTP_200_OK:
        await add_relationships(response)
    return response


@router.delete(
    "/{post_id}",
    summary="Delete a post by post ID.",
    responses=get_responses({status.HTTP_404_NOT_FOUND}),
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_post(
        post_id: str = Path(..., description="Post ID", example="5f43825c66f4c0e20cd17dc3")
) -> JSONResponse:
    response = await Mongo.delete_by__id(COLLECTION, post_id)
    if response.status_code == status.HTTP_200_OK:
        await add_relationships(response)
    return response
