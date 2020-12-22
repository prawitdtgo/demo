from pydantic import BaseModel, Field


class ExceptionError(BaseModel):
    error_code: str = Field(...,
                            title="Error code",
                            description="An error code string that can be used to classify types of errors that occur, "
                                        "and can be used to react to the errors.",
                            )
    error_description: str = Field(...,
                                   title="Error description",
                                   description="A specific error message that can help to identify the root cause of "
                                               "the error.",
                                   )


class ExceptionErrorResponse(BaseModel):
    detail: ExceptionError
