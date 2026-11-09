from fastapi import APIRouter, HTTPException, Query
from data import storage
from data.storage import get_or_404
from schemas.appointment import AppointmentResponse
from schemas.patient import PatientCreate, PatientReplace, PatientResponse, PatientUpdate
from services.appointments import has_appointments, sorted_by_time

router = APIRouter(prefix="/patients", tags=["Пациенты"])
NOT_FOUND = "Пациент не найден"


def _check_unique_phone(phone: str, exclude_id: int | None = None) -> None:
    for p in storage.patients.values():
        if p["id"] != exclude_id and p["phone"] == phone:
            raise HTTPException(409, f"Пациент с телефоном {phone} уже зарегистрирован")


@router.get("", response_model=list[PatientResponse])
def list_patients(search: str | None = Query(None, description="Поиск по имени")):
    if not search:
        return list(storage.patients.values())
    return [p for p in storage.patients.values() if search.lower() in p["full_name"].lower()]


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int):
    return get_or_404(storage.patients, patient_id, NOT_FOUND)


@router.get("/{patient_id}/appointments", response_model=list[AppointmentResponse])
def list_patient_appointments(patient_id: int):
    get_or_404(storage.patients, patient_id, NOT_FOUND)
    return sorted_by_time(a for a in storage.appointments.values() if a["patient_id"] == patient_id)


@router.post("", response_model=PatientResponse, status_code=201)
def create_patient(data: PatientCreate):
    _check_unique_phone(data.phone)
    patient_id = storage.next_id("patients")
    patient = {"id": patient_id, **data.model_dump()}
    storage.patients[patient_id] = patient
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def replace_patient(patient_id: int, data: PatientReplace):
    patient = get_or_404(storage.patients, patient_id, NOT_FOUND)
    _check_unique_phone(data.phone, exclude_id=patient_id)
    patient.update(data.model_dump())
    return patient


@router.patch("/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: int, data: PatientUpdate):
    patient = get_or_404(storage.patients, patient_id, NOT_FOUND)
    changes = data.model_dump(exclude_unset=True)
    if "phone" in changes:
        _check_unique_phone(changes["phone"], exclude_id=patient_id)
    patient.update(changes)
    return patient


@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int):
    get_or_404(storage.patients, patient_id, NOT_FOUND)
    if has_appointments(patient_id=patient_id):
        raise HTTPException(409, "Нельзя удалить пациента: у него есть записи")
    del storage.patients[patient_id]
