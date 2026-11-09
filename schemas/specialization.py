from pydantic import BaseModel, Field
from schemas.common import InputSchema, UpdateSchema


class SpecializationCreate(InputSchema):
    name: str = Field(..., min_length=2, max_length=100, examples=["Кардиолог"])
    description: str | None = Field(None, max_length=500, examples=["Заболевания сердца и сосудов"])


class SpecializationUpdate(UpdateSchema):
    NULLABLE = {"description"}

    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = Field(None, max_length=500)


class SpecializationResponse(BaseModel):
    id: int
    name: str
    description: str | None
