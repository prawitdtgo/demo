from datetime import datetime

import pytz


class DatetimeStr(str):
    """This class handles converting a datetime to a string.

    """

    @classmethod
    def __get_validators__(cls):
        """Get validators.

        """
        yield cls.validate

    @classmethod
    def validate(cls, value: datetime) -> str:
        """Validate the specified value.

        :param value: Value
        :return: Datetime in ISO format
        :raise TypeError: If the specified value is not a datetime.
        """
        if not isinstance(value, datetime):
            raise TypeError("This type must be a datetime.")

        return value.astimezone(pytz.timezone("Asia/Bangkok")).isoformat(timespec="seconds")
