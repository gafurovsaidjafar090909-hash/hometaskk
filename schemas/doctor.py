from typing import Annotated

from pydantic import BaseModel, Field

from schemas.common import InputSchema, UpdateSchema

FullName = Annotated[str, Field(min_length=3, max_length=100, examples=["Фирдавс Саидов"])]
PositiveId = Annotated[int, Field(gt=0)]
Experience = Annotated[int, Field(ge=0, le=70)]
Price = Annotated[float, Field(gt=0, examples=[150.0])]


class DoctorCreate(InputSchema):
    full_name: FullName
    specialization_id: PositiveId
    experience_years: Experience
    consultation_price: Price
    is_active: bool = True


class DoctorReplace(DoctorCreate):
    """Полное обновление (PUT): все поля обязательны."""
    is_active: bool


class DoctorUpdate(UpdateSchema):
    full_name: FullName | None = None
    specialization_id: PositiveId | None = None
    experience_years: Experience | None = None
    consultation_price: Price | None = None
    is_active: bool | None = None


class DoctorResponse(BaseModel):
    id: int
    full_name: str
    specialization_id: int
    experience_years: int
    consultation_price: float
    is_active: bool
