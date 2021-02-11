import os
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi import status
from msal import ConfidentialClientApplication, PublicClientApplication
from pydantic.networks import AnyHttpUrl

from app.models.authorization import AuthorizationCodeResponse, TokensResponse, ClientCredentialsForm, \
    RefreshTokenGrantForm, AuthorizationCodeGrantForm, SignOutResponse, AccessTokenResponse
from app.responses import get_error_response_example
from app.tokens import get_tokens_data


def __get_local_scope(scope: str) -> str:
    """Get a local scope.

    :param scope: Scope
    :return: Local scope
    """
    return f"api://{os.getenv('AZURE_AUDIENCE')}/{scope}"


async def __get_confidential_client_application(form: ClientCredentialsForm) -> ConfidentialClientApplication:
    """Get a confidential client application.

    :param form: Client form
    :return: Confidential client application
    """
    return ConfidentialClientApplication(client_id=form.client_id,
                                         client_credential=form.client_secret.get_secret_value(),
                                         authority=os.getenv("AZURE_AUTHORITY"),
                                         )


router: APIRouter = APIRouter()
__scopes: List[str] = [__get_local_scope("access_as_user")]


@router.get(
    "/authorization-url",
    summary="Get an authorization URL.",
    response_model=AuthorizationCodeResponse
)
async def get_authorization_url(
        client_id: str = Query(..., description="Client ID / Application ID"),
        redirect_uri: AnyHttpUrl = Query(..., description="Redirect URI"),
) -> dict:
    """
    Please open the returned authorization URL in a browser to authorize the specified application.

    After finish the authorization process, the authorization server will redirect to the specified redirected URL.

    ---

    <br>*These are the query strings that will be sent to the specified redirected URL in the case of successful
    and error responses.*<br><br>

    ### Successful response
    <table>
        <thead>
            <tr>
                <th width="15%">Parameter</th>
                <th width="85%">Description</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>code</td>
                <td>
                    The authorization code that the client application requested. The client application can use
                    the authorization code to request an access token for the target resource.
                    Authorization codes are short-lived, typically they expire after about 10 minutes.
                </td>
            </tr>
            <tr>
                <td>state</td>
                <td>
                    The client application should verify the state value in the request and response are identical
                    to prevent cross-site request forgery, CSRF, attacks.
                </td>
            </tr>
        </tbody>
    </table>

    ### Error response
    <table>
        <thead>
            <tr>
                <th width="15%">Parameter</th>
                <th width="85%">Description</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>error</td>
                <td>
                    An error code string that can be used to classify types of errors that occur, and can be used to
                    react to errors.
                    <p>These are possible error code strings and their root cause.</p>
                    <ul>
                        <li>
                            <b>invalid_client</b> - This error code will be presented if this web services application
                            does not expose 'access_as_user' or 'access_as_application' scope, please contact
                            the system administrator.
                        </li>
                        <li>
                            <b>interaction_required</b> - This error code will be presented if the end user is not
                            allowed to access this web services application.
                        </li>
                        <li>
                            <b>consent_required</b> - This error code will be presented if the end user does not accept
                            the client application consent request.<br>
                            (The end user presses the Cancel button on the client application consent request page.)
                        </li>
                        <li>
                            <b>access_denied</b> - This error code will be presented if the end user denies
                            the client application consent request.
                        </li>
                    </ul>
                </td>
            </tr>
            <tr>
                <td>error_description / error_subcode</td>
                <td>
                    A specific error message that can help to identify the root cause of an authentication error.
                    <p>
                        The error_subcode parameter will be returned when the error parameter is access_denied,
                        otherwise the error_description parameter will be returned.
                    </p>
                </td>
            </tr>
        </tbody>
    </table>
    """
    azure_client: PublicClientApplication = PublicClientApplication(client_id=client_id,
                                                                    authority=os.getenv("AZURE_AUTHORITY")
                                                                    )
    authorization_code_flow: dict = azure_client.initiate_auth_code_flow(scopes=__scopes, redirect_uri=redirect_uri)

    return {
        "data": {
            "authorization_url": authorization_code_flow.get("auth_uri"),
            "code_verifier": authorization_code_flow.get("code_verifier"),
            "state": authorization_code_flow.get("state")
        }
    }


@router.post(
    "/authorization-code-grant",
    summary="Redeem an authorization code for an access token.",
    description="For an SPA, please follow [this guidance]("
                "https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow#request-an"
                "-access-token).",
    response_model=TokensResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: get_error_response_example(
            error_code="invalid_grant",
            error_description="The code_verifier does not match the code_challenge supplied in "
                              "the authorization request for PKCE."
        )
    },
)
async def acquire_tokens_by_authorization_code(form: AuthorizationCodeGrantForm) -> dict:
    azure_client: ConfidentialClientApplication = await __get_confidential_client_application(form)
    access_token_response: dict = azure_client.acquire_token_by_authorization_code(
        code=form.code,
        scopes=__scopes,
        redirect_uri=form.redirect_uri,
        data={
            "code_verifier": form.code_verifier
        }
    )

    return await get_tokens_data(access_token_response)


@router.post(
    "/refresh-token-grant",
    summary="Redeem a refresh token for an access token.",
    description="For an SPA, please follow [this guidance]("
                "https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow#refresh-the"
                "-access-token).",
    response_model=TokensResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: get_error_response_example(
            error_code="invalid_client",
            error_description="Invalid client secret is provided."
        )
    },
)
async def acquire_tokens_by_refresh_token(form: RefreshTokenGrantForm) -> dict:
    azure_client: ConfidentialClientApplication = await __get_confidential_client_application(form)
    access_token_response: dict = azure_client.acquire_token_by_refresh_token(
        refresh_token=form.refresh_token,
        scopes=__scopes
    )

    return await get_tokens_data(access_token_response)


@router.get(
    "/sign-out-url",
    summary="Get a sign-out URL for sending a sign-out request.",
    description="Please open the returned sign-out URL in a browser to sign the signed-in user out of the system.",
    response_model=SignOutResponse
)
async def sign_out(
        redirect_uri: Optional[AnyHttpUrl] = Query(None, description="Redirect URI", example="http://localhost:8080")
) -> dict:
    sign_out_url: str = f"{os.getenv('AZURE_AUTHORITY')}/oauth2/v2.0/logout"

    if redirect_uri is not None:
        sign_out_url += f"?post_logout_redirect_uri={redirect_uri}"

    return {
        "data": {
            "sign_out_url": sign_out_url
        }
    }


@router.post(
    "/client-credentials-grant",
    summary="Acquire an access token by client credentials grant.",
    description="The client application consent must be approved by a global administrator first."
                "<p>**Note:** This grant type does not support an SPA.</p>",
    response_model=AccessTokenResponse,
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: get_error_response_example(
            error_code="invalid_client",
            error_description="Invalid client secret is provided."
        )
    },
)
async def acquire_tokens_by_client_credentials(form: ClientCredentialsForm) -> dict:
    azure_client: ConfidentialClientApplication = await __get_confidential_client_application(form)
    access_token_response: dict = azure_client.acquire_token_for_client(scopes=[__get_local_scope(".default")])

    return await get_tokens_data(access_token_response)
