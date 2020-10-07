from typing import Any

from bson import ObjectId


class ObjectIdStr(str):
    """This class handles converting an ObjectId to a string.

    """

    @classmethod
    def __get_validators__(cls):
        """Get validators.

        """
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> str:
        """Validate the specified value.

        :param value: Value
        :return: Object ID
        """
        if not ObjectId.is_valid(value):
            raise TypeError("%r is not an ObjectId." % value)

        return str(value)
