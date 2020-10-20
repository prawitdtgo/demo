import json
from typing import Set

from fastapi.responses import JSONResponse

from app.models.response import Message
from app.responses import Response


class TestResponse:

    def test_getting_responses(self) -> None:
        """Test getting responses.

        """
        status_codes: Set[int] = set(Response.response_messages.keys())
        result: dict = {}

        for status_code in status_codes:
            result[status_code] = {
                "model": Message,
                "content": {
                    "application/json": {"example": {"message": Response.response_messages[status_code]}}}
            }

        assert Response.get_responses(status_codes) == result

    def test_getting_responses_with_undefined_status_codes(self) -> None:
        """Test getting responses with undefined status codes.

        """
        status_codes: Set[int] = {1, 2, 3}
        result: dict = {}

        for status_code in status_codes:
            result[status_code] = {
                "model": Message,
                "content": {
                    "application/json": {"example": {"message": ""}}}
            }

        assert Response.get_responses(status_codes) == result

    def test_getting_json_response(self) -> None:
        """Test getting a JSON response.

        """
        for status_code in Response.response_messages.keys():
            response: JSONResponse = Response.get_json_response(status_code)
            assert response.status_code == status_code
            assert json.loads(response.body) == {"message": Response.response_messages[status_code]}

    def test_getting_json_response_with_undefined_status_code(self) -> None:
        """Test getting a JSON response with an undefined status code.

        """
        for status_code in {1, 2, 3}:
            response: JSONResponse = Response.get_json_response(status_code)
            assert response.status_code == status_code
            assert json.loads(response.body) == {"message": ""}
