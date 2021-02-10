from typing import Final, TypeVar


class GrantTypeRequest:
    """This class handles getting a grant type request sentence.
    """
    __grant_type: str

    def __init__(self, grant_type: str) -> None:
        """Initialize this class.

        :param grant_type: Grant type
        """
        self.__grant_type = grant_type

    def __get__(self, instance: object, instance_type: TypeVar) -> str:
        """Get a grant type request sentence.

        :param instance: Class instance
        :param instance_type: Class type
        :return: Grant type request sentence
        """
        return f"<p><b>Grant type request:</b> {self.__grant_type}</p>"


class GrantType:
    """Grant type request sentence enumeration
    """
    CLIENT_CREDENTIALS: Final[str] = GrantTypeRequest("Client Credentials")
    AUTHORIZATION_CODE: Final[str] = GrantTypeRequest("Authorization Code")
