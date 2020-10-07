from pydantic import BaseModel, Field


class Links(BaseModel):
    first_page: str = Field(..., title="First page link")
    last_page: str = Field(..., title="Last page link")
    previous_page: str = Field(None, title="Previous page link")
    next_page: str = Field(None, title="Next page link")


class Meta(BaseModel):
    current_page: int = Field(..., title="Current page", example=1)
    last_page: int = Field(..., title="Last page", example=2)
    total_records: int = Field(..., title="Total records", example=12)
    records_per_page: int = Field(..., title="Records per page", example=10)
    url: str = Field(..., title="URL")


class Pagination(BaseModel):
    links: Links
    meta: Meta
