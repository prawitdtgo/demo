import base64
import logging
import os
from typing import Set, List

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from fastapi import status
from httpx import AsyncClient, Response, ConnectTimeout, HTTPError, InvalidURL, CookieConflict, StreamError
from jwt import ExpiredSignatureError, InvalidSignatureError, InvalidIssuerError, InvalidIssuedAtError, \
    MissingRequiredClaimError, DecodeError, ImmatureSignatureError, InvalidAudienceError

from app.http_response_exception import HTTPResponseException


class JsonWebTokenException(Exception):
    pass


class JsonWebToken:
    """JSON Web Token class

    """
    __issuer: str = None
    __public_keys: List[dict] = {}
    __expired_token: dict = {
        "error_code": "expired_token",
        "error_description": "The access token has expired."
    }

    @classmethod
    async def __get_rsa_number(cls, key: str) -> int:
        """Get an RSA number from an RSA key.

        :param key: RSA key
        :return: RSA number
        """
        return int.from_bytes(bytes=base64.urlsafe_b64decode(key.encode() + b"=="), byteorder="big")

    @classmethod
    async def __get_azure_configuration(cls, url: str) -> dict:
        """Get an Azure configuration.

        :param url: Configuration URL
        :return: Azure configuration
        :raises JsonWebTokenException: If found an exception.
        """
        try:
            async with AsyncClient() as client:
                response: Response = await client.get(url)

                if response.status_code == status.HTTP_404_NOT_FOUND:
                    raise JsonWebTokenException(
                        f"Could not open {url}, please help to contact the system administrator."
                    )

                return response.json()
        except ConnectTimeout as connection_timeout:
            raise JsonWebTokenException(f"Timed out while requesting {connection_timeout.request.url}.")
        except HTTPError as connection_error:
            raise JsonWebTokenException(
                f"Found an error when requesting {connection_error.request.url}. {connection_error.__str__()}"
            )
        except (InvalidURL, CookieConflict, StreamError) as error:
            raise JsonWebTokenException(error.__str__())

    @classmethod
    async def __get_public_key(cls, kid: str) -> bytes:
        """Get a public key.

        :param kid: Key ID which is used to match a specific public key
        :return: Public key
        """
        public_key: bytes = b""

        for key in cls.__public_keys:
            if key.get("kid") == kid:
                public_key = RSAPublicNumbers(
                    e=await cls.__get_rsa_number(key.get("e")),
                    n=await cls.__get_rsa_number(key.get("n"))
                ).public_key(default_backend()).public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                break

        return public_key

    @classmethod
    async def set_up(cls) -> None:
        """Set up all configurations for validating an access token.

        :raises JsonWebTokenException: If found an exception.
        """
        configuration: dict = await cls.__get_azure_configuration(
            f"{os.getenv('AZURE_AUTHORITY')}/v2.0/.well-known/openid-configuration")
        cls.__issuer = configuration.get("issuer")
        cls.__public_keys = (await cls.__get_azure_configuration(configuration.get("jwks_uri"))).get("keys")

    @classmethod
    async def __decode_access_token(cls, access_token: str, audience: str, is_issuer_verified: bool = True,
                                    is_signature_verified: bool = True) -> dict:
        """Decode an access token.

        :param access_token: Access token
        :param audience: Audience
        :param is_issuer_verified: Is the issuer verified?
        :param is_signature_verified: Is the signature verified?
        :return: Access token claims
        :raises HTTPResponseException: If the specified access token is invalid.
        """
        try:
            header: dict = jwt.get_unverified_header(access_token)

            return jwt.decode(jwt=access_token,
                              key=await cls.__get_public_key(header.get("kid")),
                              algorithms=[header.get("alg")],
                              audience=audience,
                              issuer=cls.__issuer,
                              options={
                                  "require_exp": True,
                                  "require_iat": True,
                                  "require_nbf": True,
                                  "verify_exp": True,
                                  "verify_iat": True,
                                  "verify_nbf": True,
                                  "verify_aud": True,
                                  "verify_iss": is_issuer_verified,
                                  "verify_signature": is_signature_verified,
                              })
        except ExpiredSignatureError:
            raise HTTPResponseException(status_code=status.HTTP_401_UNAUTHORIZED, detail=cls.__expired_token)
        except (MissingRequiredClaimError, ImmatureSignatureError, InvalidIssuedAtError, InvalidAudienceError,
                InvalidIssuerError, InvalidSignatureError, DecodeError):
            raise HTTPResponseException(status_code=status.HTTP_401_UNAUTHORIZED)
        except ValueError as value_error:
            logging.error(value_error.__str__())
            raise HTTPResponseException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @classmethod
    async def get_user_identifier(cls, access_token: str, accepted_scopes: Set[str]) -> str:
        """Get the user identifier from the specified access token.

        :param access_token: Access token
        :param accepted_scopes: Accepted scopes
        :return: User identifier
        :raises HTTPResponseException: If the specified access token is invalid.
        """
        decoded_access_token: dict = await cls.__decode_access_token(access_token=access_token,
                                                                     audience=os.getenv("AZURE_AUDIENCE"),
                                                                     )

        scopes: str = decoded_access_token.get("scp")

        if scopes is None or set(scopes.split()).isdisjoint(accepted_scopes):
            raise HTTPResponseException(status_code=status.HTTP_403_FORBIDDEN)

        return decoded_access_token.get("oid")

    @classmethod
    async def validate_microsoft_graph_access_token(cls, access_token: str) -> None:
        """Validate a Microsoft Graph access token.

        :param access_token: Microsoft Graph access token
        :raises HTTPResponseException: If the specified Microsoft Graph access token is invalid.
        """
        await cls.__decode_access_token(access_token=access_token,
                                        audience="https://graph.microsoft.com",
                                        is_issuer_verified=False,
                                        is_signature_verified=False
                                        )
