import logging
from unittest import mock
from unittest.mock import AsyncMock

import pytest
import respx
from _pytest.logging import LogCaptureFixture
from fastapi import status
from httpx import Response, ConnectTimeout
from respx import MockRouter

from app.external_web_services import call_microsoft_graph_web_service
from app.http_response_exception import HTTPResponseException

mock_router: MockRouter = respx.mock(assert_all_called=False,
                                     assert_all_mocked=True,
                                     base_url="https://graph.microsoft.com/v1.0"
                                     )

__access_token: str = "eyJ0eXAiOiJKV1QiLCJub25jZSI6Im5HRUpSQU5xQTB2UExPbkFLMjJvQzFkQTFLenpvZXhuNXZGSjFTWlNONTAiLCJhbG" \
                      "ciOiJSUzI1NiIsIng1dCI6Im5PbzNaRHJPRFhFSzFqS1doWHNsSFJfS1hFZyIsImtpZCI6Im5PbzNaRHJPRFhFSzFqS1do" \
                      "WHNsSFJfS1hFZyJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20iLCJpc3MiOiJodHRwczovL3N0cy53a" \
                      "W5kb3dzLm5ldC9lZTY0ZjgyOS0xY2MyLTRmYjItOTk2ZS0yZTBmYjc4ZjVmMjkvIiwiaWF0IjoxNjEyOTkzNTI3LCJuYmY" \
                      "iOjE2MTI5OTM1MjcsImV4cCI6MTYxMjk5NzQyNywiYWlvIjoiRTJaZ1lCRE4vcElRR0psdUk3TXRaN2s2eCtrRkFBPT0iL" \
                      "CJhcHBfZGlzcGxheW5hbWUiOiJOaWx2YW5hIFdlYiBTZXJ2aWNlcyIsImFwcGlkIjoiZDY2NWVlODYtZGE0NC00ZDM2LTh" \
                      "kMzAtMGFkMmI1ZTE2YmRlIiwiYXBwaWRhY3IiOiIxIiwiaWRwIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvZWU2NGY4M" \
                      "jktMWNjMi00ZmIyLTk5NmUtMmUwZmI3OGY1ZjI5LyIsImlkdHlwIjoiYXBwIiwib2lkIjoiODAxYWYxNjYtMzA2Yi00ZGE" \
                      "xLWJhMWItOTlkODc2NmMwZWFkIiwicmgiOiIwLkFBQUFLZmhrN3NJY3NrLVpiaTRQdDQ5ZktZYnVaZFpFMmpaTmpUQUswc" \
                      "lhoYTk1eEFBQS4iLCJyb2xlcyI6WyJVc2VyLlJlYWQuQWxsIl0sInN1YiI6IjgwMWFmMTY2LTMwNmItNGRhMS1iYTFiLTk" \
                      "5ZDg3NjZjMGVhZCIsInRlbmFudF9yZWdpb25fc2NvcGUiOiJBUyIsInRpZCI6ImVlNjRmODI5LTFjYzItNGZiMi05OTZlL" \
                      "TJlMGZiNzhmNWYyOSIsInV0aSI6Ik9oc1d5bGQzV1VLS1hXLTIzZXNDQUEiLCJ2ZXIiOiIxLjAiLCJ4bXNfdGNkdCI6MTY" \
                      "xMjYyMjkxM30.ijWL9Z-CEJj9AfU0EFeqyUrm-yk2xCIC3vZgQjW3J5KlmKEpagoIC5CMEj6SLSGX8jCcPdoCS_Ryi3nK7" \
                      "Byoapg1_oYk9CqK7u8xTOFtgFJKsc1uF9e-zyKaTnlNRrq_SEo8gOEQwTh1wQTGqhcr4lDbWsPsjG0sOwaQxkdVfDTFGWM" \
                      "QwfFDIXxGlo3tOhMJDIy0nJEy6QVyO2xdvBZdRZ1OKWlg1G9efT5H4Yivdn7wdR28DbDi2d_N6iFudpekHbvfboXNn_cVr" \
                      "jDDOoINJn8c4C13XOIycLzVFZS3r04pz4W-Qk8nM-vMKPGX2IbFNZlPhf_G8kAAieTzcwXUjg"
bearer_token: str = f"Bearer {__access_token}"


@mock.patch('app.external_web_services.__get_microsoft_graph_authorization_header',
            new=AsyncMock(return_value=bearer_token)
            )
@pytest.mark.asyncio
class TestAsynchronousHTTPClient:
    """This class handles all app.external_web_services module test cases.
    """
    __authorization_header: dict = {"Authorization": bearer_token}

    @mock_router
    async def test_calling_microsoft_graph_web_service(self) -> None:
        """Test calling a Microsoft Graph web service.
        """
        method: str = "GET"
        path: str = "/me"
        returned_data: dict = {
            "businessPhones": [
                "+1 425 555 0109"
            ],
            "displayName": "Adele Vance",
            "givenName": "Adele",
            "jobTitle": "Retail Manager",
            "mail": "AdeleV@contoso.onmicrosoft.com",
            "mobilePhone": "+1 425 555 0109",
            "officeLocation": "18/2111",
            "preferredLanguage": "en-US",
            "surname": "Vance",
            "userPrincipalName": "AdeleV@contoso.onmicrosoft.com",
            "id": "87d349ed-44d7-43e1-9a83-5f2406dee5bd"
        }

        mock_router.request(method=method, url=path, headers=self.__authorization_header).mock(
            return_value=Response(status_code=status.HTTP_200_OK, json=returned_data)
        )

        assert await call_microsoft_graph_web_service(method=method, path=path) == returned_data

    @mock_router
    async def test_calling_microsoft_graph_web_service_with_parameters(self) -> None:
        """Test calling a Microsoft Graph web service with some parameters.
        """
        method: str = "GET"
        path: str = "/me"
        parameters: dict = {"$select": "givenName,surname"}
        returned_data: dict = {"givenName": "Adele", "surname": "Vance"}

        mock_router.request(method=method, url=path, params=parameters, headers=self.__authorization_header).mock(
            return_value=Response(status_code=status.HTTP_200_OK, json=returned_data)
        )

        assert await call_microsoft_graph_web_service(method=method, path=path, parameters=parameters) == returned_data

    @mock_router
    async def test_calling_microsoft_graph_web_service_with_headers(self) -> None:
        """Test calling a Microsoft Graph web service with some headers.
        """
        method: str = "GET"
        path: str = "/users"
        parameters: dict = {"$search": "displayName:Ward", "$count": "true"}
        headers: dict = {"ConsistencyLevel": "eventual"}
        returned_data: dict = {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users",
            "@odata.count": 1,
            "value": [
                {
                    "displayName": "Oscar Ward",
                    "givenName": "Oscar",
                    "mail": "oscarward@contoso.com",
                    "mailNickname": "oscward",
                    "userPrincipalName": "oscarward@contoso.com"
                }
            ]
        }
        users_header: dict = self.__authorization_header.copy()
        users_header.update(headers)

        mock_router.request(method=method, url=path, params=parameters, headers=users_header).mock(
            return_value=Response(status_code=status.HTTP_200_OK, json=returned_data)
        )

        assert await call_microsoft_graph_web_service(method=method,
                                                      path=path,
                                                      parameters=parameters,
                                                      headers=headers
                                                      ) == returned_data

    @mock_router
    async def test_calling_microsoft_graph_web_service_with_request_timeout(self, caplog: LogCaptureFixture) -> None:
        """Test calling a Microsoft Graph web service with a request timeout.
        """
        method: str = "GET"
        path: str = "/users"

        mock_router.request(method=method, url=path, headers=self.__authorization_header).mock(
            side_effect=ConnectTimeout
        )

        with pytest.raises(HTTPResponseException) as exception:
            await call_microsoft_graph_web_service(method=method, path=path)

        assert exception.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exception.value.detail.get("error_code") == "internal_server_error"

        caplog.set_level(level=logging.ERROR)

        assert caplog.messages.pop() == "Timed out while requesting https://graph.microsoft.com/v1.0/users."

    @mock_router
    async def test_calling_microsoft_graph_web_service_with_another_http_error(self, caplog: LogCaptureFixture) -> None:
        """Test calling a Microsoft Graph web service with another HTTP error.
        """
        method: str = "GET"
        path: str = "/hello"
        url: str = f"https://graph.microsoft.com/v1.0{path}"

        mock_router.request(method=method, url=path, headers=self.__authorization_header).mock(
            return_value=Response(status_code=status.HTTP_404_NOT_FOUND)
        )

        with pytest.raises(HTTPResponseException) as exception:
            await call_microsoft_graph_web_service(method=method, path=path)

        assert exception.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exception.value.detail.get("error_code") == "internal_server_error"

        caplog.set_level(level=logging.ERROR)

        assert caplog.messages.pop() == f"Found an error when requesting {url}. " \
                                        f"404 Client Error: Not Found for url: {url}\n" \
                                        "For more information check: https://httpstatuses.com/404"
