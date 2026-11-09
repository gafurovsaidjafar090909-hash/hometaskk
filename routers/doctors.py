from fastapi import APIRouter, HTTPException, Query
from data import storage
from data.storage import get_or_404
from schemas.appointment import AppointmentResponse
from schemas.doctor import DoctorCreate, DoctorReplace, DoctorResponse, DoctorUpdate
from services.appointments import has_appointments, sorted_by_time

router = APIRouter(prefix="/doctors", tags=["Врачи"])
NOT_FOUND = "Врач не найден"


def _check_specialization(spec_id: int) -> None:
    get_or_404(storage.specializations, spec_id, "Специализация не найдена")


@router.get("", response_model=list[DoctorResponse])
def list_doctors(
    specialization_id: int | None = None,
    is_active: bool | None = None,
    min_experience: int | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    search: str | None = Query(None, description="Поиск по имени"),
):
    result = []
    for d in storage.doctors.values():
        if specialization_id is not None and d["specialization_id"] != specialization_id:
            continue
        if is_active is not None and d["is_active"] != is_active:
            continue
        if min_experience is not None and d["experience_years"] < min_experience:
            continue
        if max_price is not None and d["consultation_price"] > max_price:
            continue
        if search and search.lower() not in d["full_name"].lower():
            continue
        result.append(d)
    return result


@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: int):
    return get_or_404(storage.doctors, doctor_id, NOT_FOUND)


@router.get("/{doctor_id}/appointments", response_model=list[AppointmentResponse])
def list_doctor_appointments(doctor_id: int):
    get_or_404(storage.doctors, doctor_id, NOT_FOUND)
    return sorted_by_time(a for a in storage.appointments.values() if a["doctor_id"] == doctor_id)


@router.post("", response_model=DoctorResponse, status_code=201)
def create_doctor(data: DoctorCreate):
    _check_specialization(data.specialization_id)
    doctor_id = storage.next_id("doctors")
    doctor = {"id": doctor_id, **data.model_dump()}
    storage.doctors[doctor_id] = doctor
    return doctor


@router.put("/{doctor_id}", response_model=DoctorResponse)
def replace_doctor(doctor_id: int, data: DoctorReplace):
    doctor = get_or_404(storage.doctors, doctor_id, NOT_FOUND)
    _check_specialization(data.specialization_id)
    doctor.update(data.model_dump())
    return doctor


@router.patch("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(doctor_id: int, data: DoctorUpdate):
    doctor = get_or_404(storage.doctors, doctor_id, NOT_FOUND)
    changes = data.model_dump(exclude_unset=True)
    if "specialization_id" in changes:
        _check_specialization(changes["specialization_id"])
    doctor.update(changes)
    return doctor


@router.delete("/{doctor_id}", status_code=204)
def delete_doctor(doctor_id: int):
    get_or_404(storage.doctors, doctor_id, NOT_FOUND)
    if has_appointments(doctor_id=doctor_id):
        raise HTTPException(409, "Нельзя удалить врача: у него есть записи (включая отменённые и завершённые)")
    del storage.doctors[doctor_id]
