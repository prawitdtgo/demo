from typing import Optional

import pymongo
from fastapi import APIRouter, Depends, Query
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorCollection

from app.database_connections import databases
from app.documentation import GrantTypeRequestSentence, get_accepted_user_roles_sentence
from app.json_web_token import JsonWebToken
from app.models.authorization import UserRole
from app.models.contact import ContactData, ContactCreation, ContactResponse, ContactList
from app.mongo import Mongo
from app.responses import main_endpoint_responses
from app.security import bearer_token

router: APIRouter = APIRouter()
COLLECTION: AsyncIOMotorCollection


@router.on_event("startup")
async def start_up() -> None:
    """Execute this function before execute any functions.
    """
    global COLLECTION
    COLLECTION = await databases.main_database.set_collection("contact")


@router.get(
    "",
    summary="Get contacts sorting by created time in descending order.",
    description="Contacts can be searched by first name, last name, email, or message with regular expression."
                + GrantTypeRequestSentence.AUTHORIZATION_CODE
                + get_accepted_user_roles_sentence({UserRole.CONTACT_REPORT_VIEWER}),
    response_model=ContactList,
    responses=main_endpoint_responses,
)
async def get_contacts(
        request: Request,
        authorization: HTTPAuthorizationCredentials = Depends(bearer_token),
        page: int = Query(1, description="Page", ge=1),
        records_per_page: int = Query(10, description="Records per page", ge=1),
        keyword: Optional[str] = Query(None,
                                       description="Keyword for searching contacts by first name, last name, email, "
                                                   "or message"
                                       )
) -> dict:
    await JsonWebToken.get_user_identifier(access_token=authorization.credentials,
                                           accepted_roles={UserRole.CONTACT_REPORT_VIEWER}
                                           )

    return await Mongo.list(collection=COLLECTION,
                            projection_model=ContactResponse,
                            request=request,
                            page=page,
                            records_per_page=records_per_page,
                            search_fields={"first_name", "last_name", "email", "message"},
                            keyword=keyword,
                            sort=[("created_at", pymongo.DESCENDING)]
                            )


@router.post(
    "",
    summary="Create a contact.",
    status_code=status.HTTP_201_CREATED,
    description=GrantTypeRequestSentence.CLIENT_CREDENTIALS,
    response_model=ContactData,
    responses=main_endpoint_responses,
)
async def create_contact(*,
                         request: Request,
                         response: Response,
                         authorization: HTTPAuthorizationCredentials = Depends(bearer_token),
                         contact_data: ContactCreation
                         ) -> dict:
    await JsonWebToken.validate_application_access_token(authorization.credentials)

    result: dict = await Mongo.create(COLLECTION, contact_data.dict(), ContactResponse)
    response.status_code = status.HTTP_201_CREATED
    response.headers["Location"] = str(request.url) + "/" + str(result.get("_id"))

    return result
