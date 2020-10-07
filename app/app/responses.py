from typing import Set

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

response_messages: dict = {
    status.HTTP_404_NOT_FOUND: "Not found the specified item."
}


class Message(BaseModel):
    message: str


def get_responses(status_codes: Set[int]) -> dict:
    """Get responses.

    :param status_codes: Response status codes
    :return: Responses
    """
    responses: dict = {}

    for status_code in status_codes:
        responses[status_code] = {
            "model": Message,
            "content": {"application/json": {"example": {"message": response_messages[status_code]}}}
        }

    return responses


def get_json_response(status_code: int) -> JSONResponse:
    """Get a JSON response.

    :param status_code: Response status code
    :return: JSON response
    """
    return JSONResponse(status_code=status_code, content={"message": response_messages[status_code]})
