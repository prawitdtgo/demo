from typing import List, Optional, Any

from pydantic import BaseModel, Field, validator

from app.models.pagination import Pagination
from app.models.user import UserRelationship
from app.types.datetime import DatetimeStr
from app.types.object_id import ObjectIdStr
from app.validators import validate_not_null


class PostCreation(BaseModel):
    message: str = Field(..., title="Message", min_length=10, max_length=500, example="What is quantum theory?")


class PostUpdate(BaseModel):
    message: Optional[str] = Field(None, title="Message", min_length=10, max_length=500,
                                   example="What is quantum theory?", description="This value must not be null.")

    @validator("*")
    def validate_not_null(cls, value: Any):
        return validate_not_null(value)


class PostPreResponse(BaseModel):
    id: ObjectIdStr = Field(..., title="Post ID", example="5f43825c66f4c0e20cd17dc3", alias="_id")
    message: str = Field(..., title="Message", example="What is quantum theory?")
    created_at: DatetimeStr = Field(..., title="Created time", example="2020-10-05T23:00:12+07:00")
    updated_at: DatetimeStr = Field(..., title="Updated time", example="2020-10-05T23:00:12+07:00")


class PostPreRelationships(PostPreResponse):
    owner: str = Field(..., title="Owner's identifier")


class PostRelationships(BaseModel):
    owner: UserRelationship


class PostResponse(PostPreResponse):
    relationships: PostRelationships


class PostData(BaseModel):
    data: PostResponse


class PostList(Pagination):
    data: List[PostResponse]
