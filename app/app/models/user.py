from typing import List

from pydantic import BaseModel, Field, EmailStr, validator

from app.models.pagination import Pagination
from app.mongo import Mongo
from app.types.datetime import DatetimeStr


class UserUpdate(BaseModel):
    first_name: str = Field(..., title="First name", min_length=1, max_length=50, example="Run")
    last_name: str = Field(..., title="Last name", min_length=1, max_length=50, example="Mao Li")


class UserCreation(UserUpdate):
    email: EmailStr = Field(..., title="Email", description="This value must be unique.")

    @validator("email")
    def validate_unique_email(cls, email: EmailStr) -> str:
        """Check if the specified email is unique.

        :param email: Email
        :return: Unique email
        :raise ValueError: If the specified email is duplicate.
        """
        if Mongo.is_existent("user", "email", email):
            raise ValueError("value must be unique")

        return email


class UserResponse(UserUpdate):
    email: EmailStr = Field(..., title="Email", description="This value is unique.")
    created_at: DatetimeStr = Field(..., title="Created time", example="2020-10-05T23:00:12+07:00")
    updated_at: DatetimeStr = Field(..., title="Updated time", example="2020-10-05T23:00:12+07:00")


class UserData(BaseModel):
    data: UserResponse


class UserList(Pagination):
    data: List[UserResponse]
