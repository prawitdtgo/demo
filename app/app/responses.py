from typing import Set

from fastapi import status
from fastapi.responses import JSONResponse

from app.models.response import Message


class Response:
    response_messages: dict = {
        status.HTTP_404_NOT_FOUND: "Not found the specified item."
    }

    @classmethod
    def __get_response_message(cls, status_code: int) -> str:
        """Get a response message. Returns empty if the specified status code is undefined.

        :param status_code: HTTP status code
        :return: Response message
        """
        return cls.response_messages[status_code] if status_code in cls.response_messages else ""

    @classmethod
    def get_responses(cls, status_codes: Set[int]) -> dict:
        """Get responses.

        :param status_codes: Response status codes
        :return: Responses
        """
        responses: dict = {}

        for status_code in status_codes:
            responses[status_code] = {
                "model": Message,
                "content": {"application/json": {"example": {"message": cls.__get_response_message(status_code)}}}
            }

        return responses

    @classmethod
    def get_json_response(cls, status_code: int) -> JSONResponse:
        """Get a JSON response.

        :param status_code: Response status code
        :return: JSON response
        """
        return JSONResponse(status_code=status_code, content={"message": cls.__get_response_message(status_code)})
