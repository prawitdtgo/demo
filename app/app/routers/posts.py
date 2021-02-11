from typing import Optional

from fastapi import APIRouter, Path, Query, Depends
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorCollection

from app.database_connections import databases
from app.documentation import GrantTypeRequestSentence
from app.http_response_exception import HTTPResponseException
from app.json_web_token import JsonWebToken
from app.models.post import PostList, PostData, PostCreation, PostPreRelationships, PostUpdate
from app.mongo import Mongo
from app.responses import main_endpoint_responses, subsidiary_endpoint_responses
from app.security import bearer_token
from app.types.object_id import ObjectIdStr

router: APIRouter = APIRouter()
COLLECTION: AsyncIOMotorCollection


@router.on_event("startup")
async def start_up() -> None:
    """Execute this function before execute any functions.
    """
    global COLLECTION
    COLLECTION = await databases.main_database.set_collection("post")


async def __add_owner(relationships: dict, owner: str) -> None:
    """Add an owner into the specified post's relationships data.

    :param relationships: Post's relationships data
    :param owner: Owner
    """
    relationships.update({
        "owner": {"identifier": owner}
    })


async def __add_relationships(post: dict) -> None:
    """Add relationships into the specified post data.

    :param post: Post data
    """
    relationships = post["relationships"] = {}

    await __add_owner(relationships, post.pop("owner"))


async def __prove_owner(authorization: HTTPAuthorizationCredentials, post_id: str) -> None:
    """Prove the owner of the post that is specified by post ID.

    :param authorization: Authorization header
    :param post_id: Post ID
    :raises HTTPResponseException: If the signed-in user was not the post's owner.
    """
    owner: str = await JsonWebToken.get_user_identifier(access_token=authorization.credentials)
    post: dict = await Mongo.get(COLLECTION, post_id, PostPreRelationships)

    if post.get("data").get("owner") != owner:
        raise HTTPResponseException(status_code=status.HTTP_403_FORBIDDEN)


@router.get(
    "",
    summary="Get posts sorting by updated time in descending order.",
    description="Posts can be searched by message with regular expression." + GrantTypeRequestSentence.CLIENT_CREDENTIALS,
    response_model=PostList,
    responses=main_endpoint_responses,
)
async def get_posts(
        request: Request,
        authorization: HTTPAuthorizationCredentials = Depends(bearer_token),
        page: int = Query(1, description="Page", ge=1),
        records_per_page: int = Query(10, description="Records per page", ge=1),
        keyword: Optional[str] = Query(None, description="Keyword for searching posts by message")
) -> dict:
    await JsonWebToken.validate_application_access_token(access_token=authorization.credentials)

    result: dict = await Mongo.list(collection=COLLECTION,
                                    projection_model=PostPreRelationships,
                                    request=request,
                                    page=page,
                                    records_per_page=records_per_page,
                                    search_fields={"message"},
                                    keyword=keyword
                                    )

    for post in result.get("data"):
        await __add_relationships(post)

    return result


@router.post(
    "",
    summary="Create a post.",
    status_code=status.HTTP_201_CREATED,
    description=GrantTypeRequestSentence.AUTHORIZATION_CODE,
    response_model=PostData,
    responses=main_endpoint_responses,
)
async def create_post(*,
                      request: Request,
                      response: Response,
                      authorization: HTTPAuthorizationCredentials = Depends(bearer_token),
                      post_data: PostCreation
                      ) -> dict:
    post_information: dict = post_data.dict()
    post_information["owner"] = await JsonWebToken.get_user_identifier(access_token=authorization.credentials)
    result: dict = await Mongo.create(COLLECTION, post_information, PostPreRelationships)
    response.status_code = status.HTTP_201_CREATED
    response.headers["Location"] = str(request.url) + "/" + str(result.get("_id"))

    await __add_relationships(result.get("data"))

    return result


@router.get(
    "/{post_id}",
    summary="Get a post by post ID.",
    description=GrantTypeRequestSentence.CLIENT_CREDENTIALS,
    response_model=PostData,
    responses=subsidiary_endpoint_responses,
)
async def get_post(
        authorization: HTTPAuthorizationCredentials = Depends(bearer_token),
        post_id: ObjectIdStr = Path(..., description="Post ID", example="5f43825c66f4c0e20cd17dc3")
) -> dict:
    await JsonWebToken.validate_application_access_token(access_token=authorization.credentials)

    result: dict = await Mongo.get(COLLECTION, post_id, PostPreRelationships)

    await __add_relationships(result.get("data"))

    return result


@router.patch(
    "/{post_id}",
    summary="Update an own post by post ID.",
    description=GrantTypeRequestSentence.AUTHORIZATION_CODE,
    response_model=PostData,
    responses=subsidiary_endpoint_responses,
)
async def update_post(
        *,
        authorization: HTTPAuthorizationCredentials = Depends(bearer_token),
        post_id: ObjectIdStr = Path(..., description="Post ID", example="5f43825c66f4c0e20cd17dc3"),
        post_data: PostUpdate
) -> dict:
    await __prove_owner(authorization, post_id)

    result = await Mongo.update(COLLECTION, post_id, post_data.dict(), PostPreRelationships)

    await __add_relationships(result.get("data"))

    return result


@router.delete(
    "/{post_id}",
    summary="Delete an own post by post ID.",
    description=GrantTypeRequestSentence.AUTHORIZATION_CODE,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=subsidiary_endpoint_responses,
)
async def delete_post(
        response: Response,
        authorization: HTTPAuthorizationCredentials = Depends(bearer_token),
        post_id: ObjectIdStr = Path(..., description="Post ID", example="5f43825c66f4c0e20cd17dc3")
) -> None:
    await __prove_owner(authorization, post_id)

    response.status_code = status.HTTP_204_NO_CONTENT

    await Mongo.delete(COLLECTION, post_id)
