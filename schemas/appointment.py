from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field, computed_field

from schemas.common import InputSchema, UpdateSchema

ALLOWED_DURATIONS = (15, 30, 45, 60)


class AppointmentStatus(str, Enum):
    scheduled = "scheduled"
    cancelled = "cancelled"
    completed = "completed"


def _future_utc(v: datetime) -> datetime:
    """Время обязательно со смещением (например +05:00), в будущем; храним в UTC."""
    if v.tzinfo is None:
        raise ValueError("Укажите часовой пояс, например 2026-12-01T10:00:00+05:00")
    v = v.astimezone(timezone.utc)
    if v <= datetime.now(timezone.utc):
        raise ValueError("Начало приёма должно быть в будущем")
    return v


def _allowed_duration(v: int) -> int:
    if v not in ALLOWED_DURATIONS:
        raise ValueError(f"Длительность должна быть одной из: {ALLOWED_DURATIONS} минут")
    return v


# Переиспользуемые типы: валидация описана один раз для Create и Update.
StartAt = Annotated[datetime, AfterValidator(_future_utc), Field(examples=["2026-12-01T10:00:00+05:00"])]
Duration = Annotated[int, AfterValidator(_allowed_duration), Field(examples=[30])]
Reason = Annotated[str, Field(max_length=500, examples=["Первичная консультация"])]
PositiveId = Annotated[int, Field(gt=0)]


class AppointmentCreate(InputSchema):
    patient_id: PositiveId
    doctor_id: PositiveId
    start_at: StartAt
    duration_minutes: Duration = 30
    reason: Reason | None = None


class AppointmentUpdate(UpdateSchema):
    """Статус здесь менять нельзя: для этого есть /cancel и /complete."""
    NULLABLE = {"reason"}

    doctor_id: PositiveId | None = None
    start_at: StartAt | None = None
    duration_minutes: Duration | None = None
    reason: Reason | None = None


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    start_at: datetime
    duration_minutes: int
    reason: str | None
    status: AppointmentStatus

    @computed_field
    @property
    def end_at(self) -> datetime:
        return self.start_at + timedelta(minutes=self.duration_minutes)
