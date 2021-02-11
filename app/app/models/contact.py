from typing import List

from pydantic import BaseModel, Field, EmailStr

from app.models.pagination import Pagination
from app.types.datetime import DatetimeStr
from app.types.object_id import ObjectIdStr


class ContactCreation(BaseModel):
    first_name: str = Field(..., title="First name", example="Run", min_length=1, max_length=50)
    last_name: str = Field(..., title="Last name", example="Mao Li", min_length=1, max_length=50)
    email: EmailStr = Field(..., title="Email address", example="mao_li_run@example.com")
    message: str = Field(..., title="Message", example="I would like to rent a condominium.", min_length=10,
                         max_length=500)


class ContactResponse(ContactCreation):
    id: ObjectIdStr = Field(..., title="Contact ID", example="5f43825c66f4c0e20cd17dc3", alias="_id")
    created_at: DatetimeStr = Field(..., title="Created time", example="2020-10-05T23:00:12+07:00")
    updated_at: DatetimeStr = Field(..., title="Updated time", example="2020-10-05T23:00:12+07:00")


class ContactData(BaseModel):
    data: ContactResponse


class ContactList(Pagination):
    data: List[ContactResponse]
