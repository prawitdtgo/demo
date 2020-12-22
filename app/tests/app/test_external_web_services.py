import logging

import pytest
import respx
from _pytest.logging import LogCaptureFixture
from fastapi.security import HTTPAuthorizationCredentials
from httpx import Response, ConnectTimeout
from respx import MockRouter
from starlette import status

from app.external_web_services import call_microsoft_graph_web_service
from app.http_response_exception import HTTPResponseException

mock_router: MockRouter = respx.mock(assert_all_called=False,
                                     assert_all_mocked=True,
                                     base_url="https://graph.microsoft.com/v1.0"
                                     )


@pytest.mark.asyncio
class TestAsynchronousHTTPClient:
    """This class handles all app.external_web_services module test cases.
    """
    __access_token: str = "eyJ0eXAiOiJKV1QiLCJub25jZSI6Im10Y1FvaFpGWlZROFozWTBBUlp3a0hBNjdGZ2NmUnI4d2ZqTHdHTnBpeEEiLC" \
                          "JhbGciOiJSUzI1NiIsIng1dCI6Im5PbzNaRHJPRFhFSzFqS1doWHNsSFJfS1hFZyIsImtpZCI6Im5PbzNaRHJPRFhF" \
                          "SzFqS1doWHNsSFJfS1hFZyJ9.eyJhdWQiOiJodHRwczovL2dyYXBoLm1pY3Jvc29mdC5jb20iLCJpc3MiOiJodHRwc" \
                          "zovL3N0cy53aW5kb3dzLm5ldC9jOTdkMzc5Yy1iMzA1LTQ1YjktYWE2Yi1hMWE4NWQ2ODQwZTcvIiwiaWF0IjoxNjE" \
                          "yMTg4NTI0LCJuYmYiOjE2MTIxODg1MjQsImV4cCI6MzI1MzM1NzQzOTksImFjY3QiOjAsImFjciI6IjEiLCJhY3JzI" \
                          "jpbInVybjp1c2VyOnJlZ2lzdGVyc2VjdXJpdHlpbmZvIiwidXJuOm1pY3Jvc29mdDpyZXExIiwidXJuOm1pY3Jvc29" \
                          "mdDpyZXEyIiwidXJuOm1pY3Jvc29mdDpyZXEzIiwiYzEiLCJjMiIsImMzIiwiYzQiLCJjNSIsImM2IiwiYzciLCJjO" \
                          "CIsImM5IiwiYzEwIiwiYzExIiwiYzEyIiwiYzEzIiwiYzE0IiwiYzE1IiwiYzE2IiwiYzE3IiwiYzE4IiwiYzE5Iiw" \
                          "iYzIwIiwiYzIxIiwiYzIyIiwiYzIzIiwiYzI0IiwiYzI1Il0sImFpbyI6IkFTUUEyLzhUQUFBQWM2Z0dYZUd0MElKT" \
                          "nZJckpFdTBMdEwvbVRGWXlmMFE4ZE5yMnhLazVpZnc9IiwiYW1yIjpbInB3ZCJdLCJhcHBfZGlzcGxheW5hbWUiOiJ" \
                          "XZWIgQXBwbGljYXRpb24iLCJhcHBpZCI6Ijc1ZGJlNzdmLTEwYTMtNGU1OS04NWZkLThjMTI3NTQ0ZjE3YyIsImFwc" \
                          "GlkYWNyIjoiMSIsImRldmljZWlkIjoiN2FmZjhiOWEtMDhiNy00ZmI1LWE4MTktNDQ0NTA0YzdmNjMwIiwiZmFtaWx" \
                          "5X25hbWUiOiJMaW5jb2xuIiwiZ2l2ZW5fbmFtZSI6IkFiZSAoTVNGVCkiLCJpZHR5cCI6InVzZXIiLCJpcGFkZHIiO" \
                          "iIxODQuMjUuODIuMTAxIiwibmFtZSI6ImFiZWxpIiwib2lkIjoiNzM4NjRjMzctZmY1My00NDZmLWI5ZWUtYWIyMzg" \
                          "3OTA1ZmIwIiwib25wcmVtX3NpZCI6IlMtMS01LTIxLTE2NjA5OTE5NzMtMTkwMzYzODc5MC0zNDczMDAyNjk1LTE1O" \
                          "DU2IiwicGxhdGYiOiIzIiwicHVpZCI6IjEwMDM3RkZFOTlERUUwNDciLCJyaCI6IjAuQUFBQW5EZDl5UVd6dVVXcWE" \
                          "2R29YV2hBNXhZaExyOXF0UGhIdG9Ha0lrTkdsVFp5QUFjLiIsInNjcCI6Im9wZW5pZCBwcm9maWxlIFVzZXIuUmVhZ" \
                          "CBlbWFpbCIsInN1YiI6Ikl0VE1saE1NS2ZrdWdrekpVd0xZdFVJZXBybndoWEN2ejRrNVRnbFVrcEkiLCJ0ZW5hbnR" \
                          "fcmVnaW9uX3Njb3BlIjoiQVMiLCJ0aWQiOiJmOTdkMzc5Yy1iMzA1LTQ1YjktYWE2Yi1hMWE4NWQ2ODQwZTciLCJ1b" \
                          "mlxdWVfbmFtZSI6ImFiZWxpQG1pY3Jvc29mdC5jb20iLCJ1cG4iOiJhYmVsaUBtaWNyb3NvZnQuY29tIiwidXRpIjo" \
                          "iQ1V5a1JhUmhRVXVXejFlX0lNWThBQSIsInZlciI6IjEuMCIsIndpZHMiOlsiYjc5ZmJmNGQtM2VmOS00Njg5LTgxN" \
                          "DMtNzZiMTk0ZTg1NTA5Il0sInhtc19zdCI6eyJzdWIiOiJvdDhobkVBRVJSbTJubm5XMkdjYnRrOTBpOFpxY2VCUkJ" \
                          "5Ykk0ZTIwZ2cwIn0sInhtc190Y2R0IjoxNDM2ODYyNTI0fQ.k9rgNfwrD8jotgScz6RtMTBKdzMmLBsnLJbuzZS8SC" \
                          "itN9Xevzrnvn4dVhCF7sB765KJgtqen1wQnOxRH3FpQbE7Jxm7QIsK4g7R5mxdTez88rZ_HXV2zVTxNj7je-s_dDlA" \
                          "FQk1QcrsVNbJ7MRLUpTIWcMRL0N4iiC4efK4MJgGtRiUM-8ZEaTfsC5ABM1uXwy-i1_jPgW7AM8wEe3eA-sPwMbL49" \
                          "dRSnB2e03uFu-jf7ykO7_WXQlmqcxTJhN5KcfONOKtw7noO9Osy3_av2w4UzDemaeOBPn9Yyrhpfz3jOvkigUc8DJr" \
                          "Pi_hWKugA9cdN720X1qv32pQGW5qeg"
    __authorization_credentials: HTTPAuthorizationCredentials = HTTPAuthorizationCredentials(scheme="Bearer",
                                                                                             credentials=__access_token
                                                                                             )
    __authorization_header: dict = {"Authorization": "Bearer " + __access_token}

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

        assert await call_microsoft_graph_web_service(authorization=self.__authorization_credentials,
                                                      method=method,
                                                      path=path
                                                      ) == returned_data

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

        assert await call_microsoft_graph_web_service(authorization=self.__authorization_credentials,
                                                      method=method,
                                                      path=path,
                                                      parameters=parameters
                                                      ) == returned_data

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

        assert await call_microsoft_graph_web_service(authorization=self.__authorization_credentials,
                                                      method=method,
                                                      path=path,
                                                      parameters=parameters,
                                                      headers=headers
                                                      ) == returned_data

    async def test_calling_microsoft_graph_web_service_with_invalid_access_token(self) -> None:
        """Test calling a Microsoft Graph web service with an invalid access token.
        """
        with pytest.raises(HTTPResponseException) as exception:
            await call_microsoft_graph_web_service(
                authorization=HTTPAuthorizationCredentials(scheme="Bearer", credentials="test"),
                method="GET",
                path="/me"
            )

        assert exception.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exception.value.detail.get("error_code") == "invalid_token"

    async def test_calling_microsoft_graph_web_service_with_expired_access_token(self) -> None:
        """Test calling a Microsoft Graph web service with an expired access token.
        """
        access_token: str = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Imk2bEdrM0ZaenhSY1ViMkMzbkVRN3N5SEpsWSJ9.eyJ" \
                            "hdWQiOiI2ZTc0MTcyYi1iZTU2LTQ4NDMtOWZmNC1lNjZhMzliYjEyZTMiLCJpc3MiOiJodHRwczovL2xvZ2luLm1" \
                            "pY3Jvc29mdG9ubGluZS5jb20vNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3L3YyLjAiLCJpYXQ" \
                            "iOjE1MzcyMzEwNDgsIm5iZiI6MTUzNzIzMTA0OCwiZXhwIjoxNTM3MjM0OTQ4LCJhaW8iOiJBWFFBaS84SUFBQUF" \
                            "0QWFaTG8zQ2hNaWY2S09udHRSQjdlQnE0L0RjY1F6amNKR3hQWXkvQzNqRGFOR3hYZDZ3TklJVkdSZ2hOUm53SjF" \
                            "sT2NBbk5aY2p2a295ckZ4Q3R0djMzMTQwUmlvT0ZKNGJDQ0dWdW9DYWcxdU9UVDIyMjIyZ0h3TFBZUS91Zjc5UVg" \
                            "rMEtJaWpkcm1wNjlSY3R6bVE9PSIsImF6cCI6IjZlNzQxNzJiLWJlNTYtNDg0My05ZmY0LWU2NmEzOWJiMTJlMyI" \
                            "sImF6cGFjciI6IjAiLCJuYW1lIjoiQWJlIExpbmNvbG4iLCJvaWQiOiI2OTAyMjJiZS1mZjFhLTRkNTYtYWJkMS0" \
                            "3ZTRmN2QzOGU0NzQiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJhYmVsaUBtaWNyb3NvZnQuY29tIiwicmgiOiJJIiw" \
                            "ic2NwIjoiYWNjZXNzX2FzX3VzZXIiLCJzdWIiOiJIS1pwZmFIeVdhZGVPb3VZbGl0anJJLUtmZlRtMjIyWDVyclY" \
                            "zeERxZktRIiwidGlkIjoiNzJmOTg4YmYtODZmMS00MWFmLTkxYWItMmQ3Y2QwMTFkYjQ3IiwidXRpIjoiZnFpQnF" \
                            "YTFBqMGVRYTgyUy1JWUZBQSIsInZlciI6IjIuMCJ9.pj4N-w_3Us9DrBLfpCt"

        with pytest.raises(HTTPResponseException) as exception:
            await call_microsoft_graph_web_service(
                authorization=HTTPAuthorizationCredentials(scheme="Bearer", credentials=access_token),
                method="GET",
                path="/me"
            )

        assert exception.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exception.value.detail.get("error_code") == "expired_token"

    @mock_router
    async def test_calling_microsoft_graph_web_service_with_invalid_grant_type_access_token(self) -> None:
        """Test calling a Microsoft Graph web service with an invalid grant type access token.
        """
        method: str = "GET"
        path: str = "/me"

        mock_router.request(method=method, url=path, headers=self.__authorization_header).mock(
            return_value=Response(status_code=status.HTTP_401_UNAUTHORIZED)
        )

        with pytest.raises(HTTPResponseException) as exception:
            await call_microsoft_graph_web_service(authorization=self.__authorization_credentials,
                                                   method=method,
                                                   path=path
                                                   )

        assert exception.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exception.value.detail.get("error_code") == "invalid_token"

    @mock_router
    async def test_calling_microsoft_graph_web_service_with_unauthorized_access(self) -> None:
        """Test calling a Microsoft Graph web service with unauthorized access.
        """
        method: str = "GET"
        path: str = "/me/planner/tasks"

        mock_router.request(method=method, url=path, headers=self.__authorization_header).mock(
            return_value=Response(status_code=status.HTTP_403_FORBIDDEN,
                                  json={
                                      "error": {
                                          "code": "accessDenied",
                                          "message": "Insufficient privileges to complete the operation.",
                                      }
                                  }
                                  )
        )

        with pytest.raises(HTTPResponseException) as exception:
            await call_microsoft_graph_web_service(authorization=self.__authorization_credentials,
                                                   method=method,
                                                   path=path
                                                   )

        assert exception.value.status_code == status.HTTP_403_FORBIDDEN
        assert exception.value.detail.get("error_code") == "unauthorized_access"

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
            await call_microsoft_graph_web_service(authorization=self.__authorization_credentials,
                                                   method=method,
                                                   path=path
                                                   )

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
            await call_microsoft_graph_web_service(authorization=self.__authorization_credentials,
                                                   method=method,
                                                   path=path,
                                                   )

        assert exception.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exception.value.detail.get("error_code") == "internal_server_error"

        caplog.set_level(level=logging.ERROR)

        assert caplog.messages.pop() == f"Found an error when requesting {url}. " \
                                        f"404 Client Error: Not Found for url: {url}\n" \
                                        "For more information check: https://httpstatuses.com/404"
