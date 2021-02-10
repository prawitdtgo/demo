import logging
import os
from typing import Optional

from fastapi import status
from httpx import AsyncClient, Response, ConnectTimeout, HTTPError
from msal import ConfidentialClientApplication

from app.environment import get_file_environment
from app.http_response_exception import HTTPResponseException
from app.tokens import get_tokens_data


async def __get_microsoft_graph_authorization_header() -> str:
    """Get a Microsoft graph authorization header.

    :return: Microsoft graph authorization header
    :raises HTTPResponseException: If could not get an access token for calling a Microsoft Graph web service.
    """
    azure_client: ConfidentialClientApplication = ConfidentialClientApplication(
        client_id=os.getenv("AZURE_AUDIENCE"),
        client_credential=await get_file_environment("AZURE_AUDIENCE_SECRET_FILE"),
        authority=os.getenv("AZURE_AUTHORITY")
    )
    access_token_response: dict = azure_client.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

    try:
        tokens: dict = (await get_tokens_data(access_token_response)).get("data")
        return tokens.get("token_type") + " " + tokens.get("access_token")
    except HTTPResponseException as error:
        logging.error(f"Could not get an access token for calling a Microsoft Graph web service.\n{error.detail}")
        raise HTTPResponseException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def call_microsoft_graph_web_service(method: str, path: str, parameters: Optional[dict] = None,
                                           headers: Optional[dict] = None) -> dict:
    """Call a Microsoft Graph web service.

    :param method: HTTP method
    :param path: Web service path
    :param parameters: Parameters
    :param headers: Headers
    :return: Microsoft Graph web service response
    :raises HTTPResponseException: If there were some errors during the process.
    """
    try:
        async with AsyncClient(base_url="https://graph.microsoft.com/v1.0",
                               headers={"Authorization": await __get_microsoft_graph_authorization_header()}
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
