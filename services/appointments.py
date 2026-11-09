"""Бизнес-логика записей на приём."""
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from data import storage
from data.storage import get_or_404
from schemas.appointment import AppointmentCreate, AppointmentStatus, AppointmentUpdate

SCHEDULED = AppointmentStatus.scheduled


def end_of(appt: dict) -> datetime:
    return appt["start_at"] + timedelta(minutes=appt["duration_minutes"])


def _check_doctor_active(doctor_id: int) -> None:
    doctor = get_or_404(storage.doctors, doctor_id, "Врач не найден")
    if not doctor["is_active"]:
        raise HTTPException(409, f"Врач id={doctor_id} неактивен, запись к нему невозможна")


def _check_overlap(doctor_id: int, start_at: datetime, duration: int, exclude_id: int | None = None) -> None:
    """Пересечение: new_start < existing_end AND existing_start < new_end.
    Учитываются только записи со статусом scheduled, кроме самой редактируемой."""
    new_end = start_at + timedelta(minutes=duration)
    for a in storage.appointments.values():
        if a["id"] == exclude_id or a["doctor_id"] != doctor_id or a["status"] != SCHEDULED:
            continue
        if start_at < end_of(a) and a["start_at"] < new_end:
            raise HTTPException(
                409,
                f"Врач занят: пересечение с записью id={a['id']} "
                f"({a['start_at']:%Y-%m-%d %H:%M}–{end_of(a):%H:%M} UTC)",
            )


def create_appointment(data: AppointmentCreate) -> dict:
    get_or_404(storage.patients, data.patient_id, "Пациент не найден")
    _check_doctor_active(data.doctor_id)
    _check_overlap(data.doctor_id, data.start_at, data.duration_minutes)

    appt_id = storage.next_id("appointments")
    appt = {"id": appt_id, **data.model_dump(), "status": SCHEDULED}
    storage.appointments[appt_id] = appt
    return appt


def update_appointment(appt_id: int, data: AppointmentUpdate) -> dict:
    appt = get_or_404(storage.appointments, appt_id, "Запись не найдена")
    if appt["status"] != SCHEDULED:
        raise HTTPException(409, f"Нельзя изменить запись со статусом {appt['status'].value}")

    changes = data.model_dump(exclude_unset=True)
    new = {**appt, **changes}
    if "doctor_id" in changes:
        _check_doctor_active(new["doctor_id"])
    if changes.keys() & {"doctor_id", "start_at", "duration_minutes"}:
        _check_overlap(new["doctor_id"], new["start_at"], new["duration_minutes"], exclude_id=appt_id)

    appt.update(changes)  # меняем существующий объект, а не создаём новый
    return appt


def cancel_appointment(appt_id: int) -> dict:
    appt = get_or_404(storage.appointments, appt_id, "Запись не найдена")
    if appt["status"] != SCHEDULED:
        raise HTTPException(409, f"Нельзя отменить запись со статусом {appt['status'].value}")
    appt["status"] = AppointmentStatus.cancelled
    return appt


def complete_appointment(appt_id: int) -> dict:
    appt = get_or_404(storage.appointments, appt_id, "Запись не найдена")
    if appt["status"] != SCHEDULED:
        raise HTTPException(409, f"Нельзя завершить запись со статусом {appt['status'].value}")
    if datetime.now(timezone.utc) < end_of(appt):
        raise HTTPException(409, f"Приём ещё не окончен (окончание {end_of(appt):%Y-%m-%d %H:%M} UTC)")
    appt["status"] = AppointmentStatus.completed
    return appt


def has_appointments(*, doctor_id: int | None = None, patient_id: int | None = None) -> bool:
    """Есть ли хоть одна запись (любого статуса) у врача или пациента."""
    return any(
        (doctor_id is not None and a["doctor_id"] == doctor_id)
        or (patient_id is not None and a["patient_id"] == patient_id)
        for a in storage.appointments.values()
    )


def sorted_by_time(items) -> list[dict]:
    return sorted(items, key=lambda a: a["start_at"])
