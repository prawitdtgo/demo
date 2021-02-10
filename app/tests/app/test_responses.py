from typing import Set
from unittest import mock

import pytest

from app.models.exception import ErrorResponse
from app.responses import get_responses, get_response_detail, get_error_response_example


@mock.patch('app.responses.__response_details', {
    401: {
        "error_code": "invalid_token",
        "error_description": "The access token was invalid."
    },
    902: {
        "error_code": "item_not_found",
        "error_description": "The specified item was not found."
    },
    903: {
        "error_code": "unauthorized_access",
        "error_description": "There were insufficient privileges to complete the operation."
    }
})
class TestResponses:
    """This class handles all app.responses module test cases.
    """

    def test_getting_response_detail(self) -> None:
        """Test getting a response detail.
        """
        assert get_response_detail(902) == {
            "error_code": "item_not_found",
            "error_description": "The specified item was not found."
        }

    def test_getting_response_detail_with_undefined_status_code(self) -> None:
        """Test getting a response detail with an undefined status code.
        """
        status_code: int = 901
        with pytest.raises(ValueError, match=f"The specified status code, {status_code}, is undefined."):
            get_response_detail(status_code)

    def test_getting_responses(self) -> None:
        """Test getting responses.
        """
        assert get_responses({401, 903}) == {
            401: {
                "model": ErrorResponse,
                "content": {
                    "application/json": {
                        "example": {
                            "detail": {
                                "error_code": "invalid_token",
                                "error_description": "The access token was invalid."
                            }
                        }
                    }
                }
            },
            903: {
                "model": ErrorResponse,
                "content": {
                    "application/json": {
                        "example": {
                            "detail": {
                                "error_code": "unauthorized_access",
                                "error_description": "There were insufficient privileges to complete the operation."
                            }
                        }
                    }
                }
            }
        }

    def test_getting_responses_with_undefined_status_codes(self) -> None:
        """Test getting responses with undefined status codes.
        """
        status_codes: Set[int] = {400, 403, 901}

        with pytest.raises(ValueError, match=f"The specified status code, 400, is undefined."):
            get_responses(status_codes)

    def test_getting_error_response_example(self) -> None:
        """Test getting an error response example.
        """
        error_code: str = "invalid_client"
        error_description: str = "Invalid client secret is provided."

        assert get_error_response_example(error_code=error_code, error_description=error_description) == {
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "error_code": error_code,
                            "error_description": error_description
                        }
                    }
                }
            }
        }
