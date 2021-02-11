from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.documentation import GrantTypeRequestSentence
from app.external_web_services import call_microsoft_graph_web_service
from app.json_web_token import JsonWebToken
from app.models.user import UserData
from app.responses import main_endpoint_responses
from app.security import bearer_token

router = APIRouter()


@router.get(
    "/me",
    summary="Get a signed-in user's profile.",
    description=GrantTypeRequestSentence.AUTHORIZATION_CODE,
    responses=main_endpoint_responses,
    response_model=UserData
)
async def get_signed_in_user_profile(authorization: HTTPAuthorizationCredentials = Depends(bearer_token)) -> dict:
    identifier: str = await JsonWebToken.get_user_identifier(authorization.credentials)
    user: dict = await call_microsoft_graph_web_service(method="GET",
                                                        path=f"/users/{identifier}",
                                                        parameters={
                                                            "$select": "id, givenName, surname, mail, jobTitle"
                                                        }
                                                        )

    return {
        "data": {
            "identifier": user.get("id"),
            "first_name": user.get("givenName"),
            "last_name": user.get("surname"),
            "email": user.get("mail"),
            "job_title": user.get("jobTitle")
        }
    }
