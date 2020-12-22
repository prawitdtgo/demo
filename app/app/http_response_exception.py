from typing import Optional, Dict, Any

from fastapi import HTTPException, status

from app.responses import get_response_detail


class HTTPResponseException(HTTPException):
    """HTTP response exception class
    """

    def __init__(
            self,
            status_code: int,
            detail: Optional[Dict[str, str]] = None,
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initiate an exception response class object.

        :param status_code: Status code
        :param detail: Detail
        :param headers: Headers
        :raises ValueError: If the specified status code is undefined.
        """
        if detail is None:
            detail = get_response_detail(status_code)

        if status_code == status.HTTP_401_UNAUTHORIZED:

            additional_header: dict = {"WWW-Authenticate": "Bearer"}

            if headers is None:
                headers = additional_header
            else:
                headers.update(additional_header)

        super().__init__(status_code=status_code, detail=detail, headers=headers)
