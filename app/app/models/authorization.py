import os

from pydantic import Field, AnyHttpUrl, SecretStr
from pydantic.main import BaseModel


class AuthorizationCodeData(BaseModel):
    authorization_url: str = Field(...,
                                   title="Authorization URL",
                                   example="https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
                                           "?client_id=bf2e2116-b46a-47f8-b681-a42243469536&response_type=code"
                                           "&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Findex.html"
                                           "&scope=https%3A%2F%2Fgraph.microsoft.com%2FUser.Read+offline_access"
                                           "+openid+profile"
                                           "&state=cmpgoPIfSADJQOzj"
                                           "&code_challenge=KNPStOPNGEw9aZwLRh8jX9l3_95t9_A-gh-Rt7smqVw"
                                           "&code_challenge_method=S256"
                                           "&nonce=4d31d7d8cf1d56805a9031b28ba517af3487b052e87267a1882e9695b431f7ba"
                                   )
    code_verifier: str = Field(...,
                               title="Code verifier",
                               description="This must be sent when redeem an authorization code for an access token.",
                               example="Vik-lL~jqfospBgR25hGKWyT7Q8_xMPAYrDvCenSJa9"
                               )
    state: str = Field(...,
                       title="State",
                       description="The state value that will be sent to the authorization server by "
                                   "the authorization URL. The client application should verify this state value and "
                                   "the response's state value are identical to prevent cross-site request forgery, "
                                   "CSRF, attacks.",
                       example="cmpgoPIfSADJQOzj"
                       )


class AuthorizationCodeResponse(BaseModel):
    data: AuthorizationCodeData


class ClientCredentialsForm(BaseModel):
    client_id: str = Field(..., title="Client ID")
    client_secret: SecretStr = Field(..., title="Client secret")


class AuthorizationCodeGrantForm(ClientCredentialsForm):
    redirect_uri: AnyHttpUrl = Field(...,
                                     title="Redirect URI",
                                     description="The same redirect URI value that was used to acquire "
                                                 "the authorization code.",
                                     example="https://login.microsoftonline.com/common/oauth2/nativeclient"
                                     )
    code: str = Field(...,
                      title="Authorization code",
                      description="The authorization code that was received from the authorization server."
                      )
    code_verifier: str = Field(...,
                               title="Code verifier",
                               description="The code verifier that was received from "
                                           f"GET {os.getenv('API_BASE_URL')}/oauth2/authorization-url."
                               )


class RefreshTokenGrantForm(ClientCredentialsForm):
    refresh_token: str = Field(...,
                               title="Refresh token",
                               description="The refresh token that was received from "
                                           f"POST {os.getenv('API_BASE_URL')}/oauth2/authorization-code-grant."
                               )


class AccessTokenData(BaseModel):
    token_type: str = Field(..., title="Token type", example="Bearer")
    access_token: str = Field(..., title="Access token", description="Use this token to access these web services.")
    access_token_expiration: int = Field(...,
                                         title="Access token expiration",
                                         description="How long the access token is valid (in seconds).",
                                         example=3599
                                         )


class AccessTokenResponse(BaseModel):
    data: AccessTokenData


class TokensData(AccessTokenData):
    scope: str = Field(...,
                       title="Scopes",
                       description="A space-separated list of scopes that the access token is valid for.",
                       )
    refresh_token: str = Field(...,
                               title="Refresh token",
                               description="Use this token to acquire additional access tokens "
                                           "after the current access token expires. Refresh tokens are long-lived, "
                                           "and can be used to retain access to these web services "
                                           "for extended periods of time."
                               )


class TokensResponse(BaseModel):
    data: TokensData


class SignOutData(BaseModel):
    sign_out_url: AnyHttpUrl = Field(...,
                                     title="Sign-out URL",
                                     description="The URL for signing the signed-in user out of the system.",
                                     example="https://login.microsoftonline.com/common/oauth2/v2.0/logout"
                                             "?post_logout_redirect_uri=http://localhost:8080"
                                     )


class SignOutResponse(BaseModel):
    data: SignOutData
