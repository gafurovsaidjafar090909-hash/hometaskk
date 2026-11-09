import datetime as dt
from fastapi import APIRouter, Query
from data import storage
from data.storage import get_or_404
from schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentStatus, AppointmentUpdate
from services import appointments as service

router = APIRouter(prefix="/appointments", tags=["Записи на приём"])


@router.get("", response_model=list[AppointmentResponse])
def list_appointments(
    doctor_id: int | None = None,
    patient_id: int | None = None,
    status: AppointmentStatus | None = None,
    date: dt.date | None = Query(None, description="День приёма YYYY-MM-DD (по UTC)"),
):
    result = []
    for a in storage.appointments.values():
        if doctor_id is not None and a["doctor_id"] != doctor_id:
            continue
        if patient_id is not None and a["patient_id"] != patient_id:
            continue
        if status is not None and a["status"] != status:
            continue
        if date is not None and a["start_at"].date() != date:
            continue
        result.append(a)
    return service.sorted_by_time(result)


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int):
    return get_or_404(storage.appointments, appointment_id, "Запись не найдена")


@router.post("", response_model=AppointmentResponse, status_code=201)
def create_appointment(data: AppointmentCreate):
    return service.create_appointment(data)


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(appointment_id: int, data: AppointmentUpdate):
    return service.update_appointment(appointment_id, data)


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(appointment_id: int):
    return service.cancel_appointment(appointment_id)


@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
def complete_appointment(appointment_id: int):
    return service.complete_appointment(appointment_id)
