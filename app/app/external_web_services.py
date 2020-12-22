import logging
from typing import Optional

from fastapi.security import HTTPAuthorizationCredentials
from httpx import AsyncClient, Response, ConnectTimeout, HTTPError
from starlette import status

from app.http_response_exception import HTTPResponseException
from app.json_web_token import JsonWebToken


async def call_microsoft_graph_web_service(authorization: HTTPAuthorizationCredentials, method: str, path: str,
                                           parameters: Optional[dict] = None, headers: Optional[dict] = None) -> dict:
    """Call a Microsoft Graph web service.

    :param authorization: Authorization header
    :param method: HTTP method
    :param path: Web service path
    :param parameters: Parameters
    :param headers: Headers
    :return: Microsoft Graph web service response
    :raises HTTPResponseException: If there were some errors in the response.
    """
    await JsonWebToken.validate_microsoft_graph_access_token(authorization.credentials)

    authorization_header: str = authorization.scheme + " " + authorization.credentials

    if headers is None:
        headers = {}

    if parameters is None:
        parameters = {}

    try:
        async with AsyncClient(base_url="https://graph.microsoft.com/v1.0",
                               headers={"Authorization": authorization_header}
                               ) as client:
            response: Response = await client.request(method=method, url=path, params=parameters, headers=headers)

            if response.status_code == status.HTTP_200_OK:
                return response.json()
            elif response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]:
                raise HTTPResponseException(status_code=response.status_code)
            else:
                response.raise_for_status()
    except ConnectTimeout as connection_timeout:
        logging.error(f"Timed out while requesting {connection_timeout.request.url}.")
        raise HTTPResponseException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except HTTPError as connection_error:
        logging.error(f"Found an error when requesting {connection_error.request.url}. {connection_error.__str__()}")
        raise HTTPResponseException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
