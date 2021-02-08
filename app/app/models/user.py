from typing import Union

from pydantic import BaseModel, Field, EmailStr


class UserRelationship(BaseModel):
    identifier: str = Field(..., title="User identifier")


class UserResponse(UserRelationship):
    first_name: Union[str, None] = Field(..., title="First name", example="Run")
    last_name: Union[str, None] = Field(..., title="Last name", example="Mao Li")
    email: Union[EmailStr, None] = Field(..., title="Email address", example="mao_li_run@example.com")
    job_title: Union[str, None] = Field(..., title="Job title", example="System Developer")


class UserData(BaseModel):
    data: UserResponse
