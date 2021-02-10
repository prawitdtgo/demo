import re

from fastapi import status

from app.http_response_exception import HTTPResponseException


async def get_tokens_data(access_token_response: dict) -> dict:
    """Get tokens data.

    :param access_token_response: Access token response
    :return: Tokens data
    :raises HTTPResponseException: If found an error in the access token response.
    """
    if "error" in access_token_response:
        raise HTTPResponseException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": access_token_response.get("error"),
                "error_description":
                    re.split(": ", re.split("\r\n", access_token_response.get("error_description"), 1)[0], 1)[1]
            }
        )

    return {
        "data": {
            "token_type": access_token_response.get("token_type"),
            "access_token": access_token_response.get("access_token"),
            "access_token_expiration": access_token_response.get("expires_in"),
            "scope": access_token_response.get("scope"),
            "refresh_token": access_token_response.get("refresh_token"),
        }
    }
