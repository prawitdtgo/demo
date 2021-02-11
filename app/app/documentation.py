from typing import Final, TypeVar, Set, Union, Type

from app.models.authorization import UserRole


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


class GrantTypeRequestSentence:
    """Grant type request sentence enumeration
    """
    CLIENT_CREDENTIALS: Final[str] = GrantTypeRequest("Client Credentials")
    AUTHORIZATION_CODE: Final[str] = GrantTypeRequest("Authorization Code")


def get_accepted_user_roles_sentence(user_roles: Union[Set[UserRole], Type[UserRole]]) -> str:
    """Get an accepted user role sentence.

    :param user_roles: User roles
    :return: Accepted user role sentence
    """
    accepted_user_roles: str = ""

    for user_role in user_roles:
        accepted_user_roles += user_role.value + ", "

    accepted_user_roles = accepted_user_roles.rsplit(",", 1)[0]

    return f"<p><b>Accepted user roles:</b> {accepted_user_roles}</p>"
