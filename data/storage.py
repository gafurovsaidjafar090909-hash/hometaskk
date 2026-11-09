"""Хранилище в памяти. Данные пропадают после перезапуска сервера.

Запускать в одном процессе (без --workers): у каждого процесса была бы своя копия данных.
"""
from itertools import count

from fastapi import HTTPException

specializations: dict[int, dict] = {}
doctors: dict[int, dict] = {}
patients: dict[int, dict] = {}
appointments: dict[int, dict] = {}

# Счётчики только растут, поэтому ID после удаления не используется повторно.
_counters = {name: count(1) for name in ("specializations", "doctors", "patients", "appointments")}


def next_id(entity: str) -> int:
    return next(_counters[entity])


def get_or_404(collection: dict[int, dict], item_id: int, message: str) -> dict:
    item = collection.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"{message} (id={item_id})")
    return item
