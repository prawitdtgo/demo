from typing import Set

from fastapi import status

from app.models.exception import ErrorResponse

__response_details: dict = {
    status.HTTP_401_UNAUTHORIZED: {
        "error_code": "invalid_token",
        "error_description": "The access token is invalid."
    },
    status.HTTP_403_FORBIDDEN: {
        "error_code": "unauthorized_access",
        "error_description": "There were insufficient privileges to complete the operation."
    },
    status.HTTP_404_NOT_FOUND: {
        "error_code": "item_not_found",
        "error_description": "The specified item was not found."
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "error_code": "internal_server_error",
        "error_description": "There is an internal server error, please try again or contact the system administrator."
    }
}


def get_response_detail(status_code: int) -> dict:
    """Get a response detail.

    :param status_code: Status code
    :return: Response detail
    :raises ValueError: If the specified status code is undefined.
    """
    detail: dict = __response_details.get(status_code)

    if detail is None:
        raise ValueError(f"The specified status code, {status_code}, is undefined.")

    return detail


def get_responses(status_codes: Set[int]) -> dict:
    """Get responses.

    :param status_codes: Response status codes
    :return: Responses
    """
    responses: dict = {}

    for status_code in status_codes:
        error: dict = get_response_detail(status_code)
        responses[status_code] = get_error_response_example(error_code=error.get("error_code"),
                                                            error_description=error.get("error_description")
                                                            )

    return responses


def get_error_response_example(error_code: str, error_description: str) -> dict:
    """Get an error response example.

    :param error_code: Error code
    :param error_description: Error description
    :return: Error response example
    """
    return {
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


__main_response_codes: set = {status.HTTP_500_INTERNAL_SERVER_ERROR,
                              status.HTTP_401_UNAUTHORIZED,
                              status.HTTP_403_FORBIDDEN
                              }
main_endpoint_responses: dict = get_responses(__main_response_codes)
subsidiary_endpoint_responses: dict = get_responses(__main_response_codes.union({status.HTTP_404_NOT_FOUND}))
