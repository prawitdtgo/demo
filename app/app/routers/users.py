from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.external_web_services import call_microsoft_graph_web_service
from app.models.user import UserData
from app.responses import main_endpoint_responses
from app.security import bearer_token

router = APIRouter()


@router.get(
    "/me",
    summary="Get a signed-in user's profile.",
    description="**Grant type request:** Authorization code"
                "<p>**Scope request:** https://graph.microsoft.com/User.Read</p>",
    responses=main_endpoint_responses,
    response_model=UserData
)
async def get_signed_in_user_profile(authorization: HTTPAuthorizationCredentials = Depends(bearer_token)) -> dict:
    result = await call_microsoft_graph_web_service(authorization=authorization,
                                                    method="GET",
                                                    path="/me",
                                                    parameters={
                                                        "$select": "id, givenName, surname, mail, jobTitle"
                                                    }
                                                    )

    return {
        "data": {
            "identifier": result.get("id"),
            "first_name": result.get("givenName"),
            "last_name": result.get("surname"),
            "email": result.get("mail"),
            "job_title": result.get("jobTitle")
        }
    }
