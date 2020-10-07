from typing import Any

from pydantic import NoneIsNotAllowedError


def validate_not_null(value: Any) -> Any:
    """Check if the specified value is not null.

    :param value: Value
    :return: Value
    :raise NoneIsNotAllowedError: If the specified value is null.
    """
    if value is None:
        raise NoneIsNotAllowedError()

    return value
