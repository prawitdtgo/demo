from pydantic import BaseModel, Field, EmailStr


class UserRelationship(BaseModel):
    identifier: str = Field(..., title="User identifier")


class UserResponse(UserRelationship):
    first_name: str = Field(..., title="First name", example="Run")
    last_name: str = Field(..., title="Last name", example="Mao Li")
    email: EmailStr = Field(..., title="Email address", example="mao_li_run@example.com")
    job_title: str = Field(..., title="Job title", example="System Developer")


class UserData(BaseModel):
    data: UserResponse
