from fastapi import HTTPException
from fastapi import status
from fastapi.requests import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.http_response_exception import HTTPResponseException


class BearerToken(HTTPBearer):
    """A security class for getting a Bearer token
    """

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        """Get a Bearer token.

        :param request: HTTP request
        :return: Bearer token
        :raises HTTPException: If the request's Authorization header is invalid.
        """
        try:
            return await super().__call__(request)
        except HTTPException:
            raise HTTPResponseException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error_code": "authorization_header_not_found",
                    "error_description": "An Authorization header must be included in the request."
                }
            )


bearer_token: BearerToken = BearerToken()
