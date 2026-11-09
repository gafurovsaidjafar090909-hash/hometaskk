from datetime import date
from typing import Annotated

from pydantic import AfterValidator, BaseModel, EmailStr, Field, StringConstraints

from schemas.common import InputSchema, UpdateSchema


def _not_future(v: date) -> date:
    if v > date.today():
        raise ValueError("Дата рождения не может быть в будущем")
    return v


FullName = Annotated[str, Field(min_length=3, max_length=100)]
Phone = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
BirthDate = Annotated[date, AfterValidator(_not_future)]


class PatientCreate(InputSchema):
    full_name: FullName = Field(examples=["Мухаммад Алиев"])
    phone: Phone = Field(examples=["+992900001122"])
    email: EmailStr | None = Field(None, examples=["patient@example.com"])
    birth_date: BirthDate | None = Field(None, examples=["2002-05-12"])


class PatientReplace(PatientCreate):
    """Полное обновление (PUT): необязательные поля, которые не переданы, станут null."""


class PatientUpdate(UpdateSchema):
    NULLABLE = {"email", "birth_date"}

    full_name: FullName | None = None
    phone: Phone | None = None
    email: EmailStr | None = None
    birth_date: BirthDate | None = None


class PatientResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    email: EmailStr | None
    birth_date: date | None
