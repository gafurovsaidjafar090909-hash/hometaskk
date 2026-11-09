from fastapi import APIRouter, HTTPException

from data import storage
from data.storage import get_or_404
from schemas.specialization import SpecializationCreate, SpecializationResponse, SpecializationUpdate

router = APIRouter(prefix="/specializations", tags=["Специализации"])
NOT_FOUND = "Специализация не найдена"


def _check_unique_name(name: str, exclude_id: int | None = None) -> None:
    for s in storage.specializations.values():
        if s["id"] != exclude_id and s["name"].lower() == name.lower():
            raise HTTPException(409, f"Специализация «{name}» уже существует")


@router.get("", response_model=list[SpecializationResponse])
def list_specializations():
    return list(storage.specializations.values())


@router.get("/{specialization_id}", response_model=SpecializationResponse)
def get_specialization(specialization_id: int):
    return get_or_404(storage.specializations, specialization_id, NOT_FOUND)


@router.post("", response_model=SpecializationResponse, status_code=201)
def create_specialization(data: SpecializationCreate):
    _check_unique_name(data.name)
    specialization_id = storage.next_id("specializations")
    spec = {"id": specialization_id, **data.model_dump()}
    storage.specializations[specialization_id] = spec
    return spec


@router.patch("/{specialization_id}", response_model=SpecializationResponse)
def update_specialization(specialization_id: int, data: SpecializationUpdate):
    spec = get_or_404(storage.specializations, specialization_id, NOT_FOUND)
    changes = data.model_dump(exclude_unset=True)
    if "name" in changes:
        _check_unique_name(changes["name"], exclude_id=specialization_id)
    spec.update(changes)
    return spec


@router.delete("/{specialization_id}", status_code=204)
def delete_specialization(specialization_id: int):
    get_or_404(storage.specializations, specialization_id, NOT_FOUND)
    if any(d["specialization_id"] == specialization_id for d in storage.doctors.values()):
        raise HTTPException(409, "Нельзя удалить специализацию: к ней привязаны врачи")
    del storage.specializations[specialization_id]
