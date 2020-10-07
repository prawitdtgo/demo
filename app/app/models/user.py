from typing import List, Optional, Any

from pydantic import BaseModel, Field, EmailStr, validator

from app.models.pagination import Pagination
from app.mongo import Mongo
from app.types.datetime import DatetimeStr
from app.validators import validate_not_null


class UserCreation(BaseModel):
    email: EmailStr = Field(..., title="Email", description="This value must be unique.")
    first_name: str = Field(..., title="First name", min_length=1, max_length=50, example="Run")
    last_name: str = Field(..., title="Last name", min_length=1, max_length=50, example="Mao Li")

    @validator("email")
    def validate_unique_email(cls, email: EmailStr) -> str:
        """Check if the specified email is unique.

        :param email: Email
        :return: Unique email
        :raise ValueError: If the specified email is duplicate.
        """
        if Mongo.is_existent("user", "email", email):
            raise ValueError("This value must be unique.")

        return email


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, title="First name", min_length=1, max_length=50, example="Run",
                                      description="This value must not be null.")
    last_name: Optional[str] = Field(None, title="Last name", min_length=1, max_length=50, example="Mao Li",
                                     description="This value must not be null.")

    @validator("*")
    def validate_not_null(cls, value: Any):
        return validate_not_null(value)


class UserRelationship(BaseModel):
    email: EmailStr = Field(..., title="Email")
    first_name: str = Field(..., title="First name", example="Run")
    last_name: str = Field(..., title="Last name", example="Mao Li")


class UserResponse(UserRelationship):
    created_at: DatetimeStr = Field(..., title="Created time", example="2020-10-05T23:00:12+07:00")
    updated_at: DatetimeStr = Field(..., title="Updated time", example="2020-10-05T23:00:12+07:00")


class UserData(BaseModel):
    data: UserResponse


class UserList(Pagination):
    data: List[UserResponse]
