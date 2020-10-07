from typing import List

from pydantic import BaseModel, Field, EmailStr, validator

from app.models.pagination import Pagination
from app.mongo import Mongo
from app.types.datetime import DatetimeStr
from app.types.object_id import ObjectIdStr


class PostUpdate(BaseModel):
    message: str = Field(..., title="Message", min_length=10, max_length=500, example="What is quantum theory?")


class PostCreation(PostUpdate):
    owner: EmailStr = Field(..., title="Owner's email",
                            description="This value must exist in GET /api/v1/users web service.")

    @validator("owner")
    def validate_existent_email(cls, email: EmailStr) -> str:
        """Check if the specified email is existent.

        :param email: Email
        :return: Existent email
        :raise ValueError: If the specified email is not existent.
        """
        if not Mongo.is_existent("user", "email", email):
            raise ValueError("value must exist in GET /api/v1/users web service")

        return email


class PostOwner(BaseModel):
    first_name: str = Field(..., title="First name", example="Run")
    last_name: str = Field(..., title="Last name", example="Mao Li")
    email: EmailStr = Field(..., title="Email")


class PostRelationships(BaseModel):
    owner: PostOwner


class PostPreResponse(PostUpdate):
    id: ObjectIdStr = Field(..., title="Post ID", example="5f43825c66f4c0e20cd17dc3", alias="_id")
    created_at: DatetimeStr = Field(..., title="Created time", example="2020-10-05T23:00:12+07:00")
    updated_at: DatetimeStr = Field(..., title="Updated time", example="2020-10-05T23:00:12+07:00")


class PostDataResponse(PostPreResponse):
    owner: EmailStr = Field(..., title="Owner's email")


class PostResponse(PostPreResponse):
    relationships: PostRelationships


class PostData(BaseModel):
    data: PostResponse


class PostList(Pagination):
    data: List[PostResponse]
