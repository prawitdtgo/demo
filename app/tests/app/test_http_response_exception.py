from unittest import mock

import pytest

from app.http_response_exception import HTTPResponseException


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
class TestHTTPResponseException:
    """This class handles all app.http_response_exception.HTTPResponseException class test cases.
    """

    def test_exception_response(self) -> None:
        """Test an exception response.
        """
        status_code: int = 902
        result: HTTPResponseException = HTTPResponseException(status_code=status_code)

        assert result.status_code == status_code
        assert result.detail == {
            "error_code": "item_not_found",
            "error_description": "The specified item was not found."
        }
        assert result.headers is None

    def test_exception_response_with_custom_detail_value(self) -> None:
        """Test an exception response with a custom detail value.
        """
        status_code: int = 902
        detail: dict = {
            "error_code": "invalid_grant",
            "error_description": "The code_verifier does not match the code_challenge."
        }
        result: HTTPResponseException = HTTPResponseException(status_code=status_code, detail=detail)

        assert result.status_code == status_code
        assert result.detail == detail
        assert result.headers is None

    def test_exception_response_with_invalid_custom_detail_value(self) -> None:
        """Test an exception response with an invalid custom detail value.
        """
        status_code: int = 902
        detail: dict = {
            "error": "invalid_grant",
            "error_description": "The code_verifier does not match the code_challenge."
        }

        with pytest.raises(ValueError, match="The detail's keys must be error_code and error_description."):
            HTTPResponseException(status_code=status_code, detail=detail)

    def test_exception_response_with_headers(self) -> None:
        """Test an exception response with headers.
        """
        status_code: int = 902
        headers: dict = {
            "custom-code": "item_not_found",
            "custom-description": "The specified item was not found.",
        }
        result: HTTPResponseException = HTTPResponseException(status_code=status_code, headers=headers)

        assert result.status_code == status_code
        assert result.detail == {
            "error_code": "item_not_found",
            "error_description": "The specified item was not found."
        }
        assert result.headers == headers

    def test_exception_response_with_status_code_401(self) -> None:
        """Test an exception response with status code 401.
        """
        status_code: int = 401
        result: HTTPResponseException = HTTPResponseException(status_code=status_code)

        assert result.status_code == status_code
        assert result.detail == {
            "error_code": "invalid_token",
            "error_description": "The access token was invalid."
        }
        assert result.headers == {"WWW-Authenticate": "Bearer"}

    def test_exception_response_with_status_code_401_and_headers(self) -> None:
        """Test an exception response with status code 401 and headers.
        """
        status_code: int = 401
        headers: dict = {
            "custom-code": "item_not_found",
            "custom-description": "The specified item was not found.",
        }
        result: HTTPResponseException = HTTPResponseException(status_code=status_code, headers=headers)

        assert result.status_code == status_code
        assert result.detail == {
            "error_code": "invalid_token",
            "error_description": "The access token was invalid."
        }
        assert result.headers == {
            "custom-code": "item_not_found",
            "custom-description": "The specified item was not found.",
            "WWW-Authenticate": "Bearer"
        }

    def test_exception_response_with_undefined_status_code(self) -> None:
        """Test an exception response with an undefined status code.

        """
        with pytest.raises(ValueError):
            HTTPResponseException(status_code=100)
