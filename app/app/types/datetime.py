from datetime import datetime
from typing import Any, Generator

from tzlocal import get_localzone


class DatetimeStr(str):
    """This class handles converting a datetime to a string.
    """

    @classmethod
    def __get_validators__(cls) -> Generator:
        """Get validators.
        """
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> str:
        """Validate the specified value.

        :param value: Value
        :return: Datetime in ISO format
        :raise TypeError: If the specified value is not a datetime.
        """
        if not isinstance(value, datetime):
            raise TypeError("%r is not a datetime." % value)

        return value.astimezone(get_localzone()).isoformat(timespec="seconds")
