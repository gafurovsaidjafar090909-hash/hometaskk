# MedBook API — онлайн-запись к врачам

Учебный REST API на FastAPI и Pydantic v2. Данные хранятся только в памяти Python и теряются после перезапуска сервера. Не храните здесь настоящие персональные или медицинские данные.

## Запуск

Нужен Python 3.11 или новее.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Swagger-документация: http://127.0.0.1:8000/docs

Запускайте в **одном процессе** (без `--workers`): у каждого процесса было бы своё отдельное хранилище.

## Структура

```text
main.py              — приложение, подключение роутеров с префиксом /api/v1
data/storage.py      — коллекции в памяти, генерация ID, get_or_404
schemas/             — Pydantic-схемы ...Create / ...Update / ...Replace / ...Response
routers/             — эндпоинты, по одному файлу на сущность
services/appointments.py — бизнес-логика записей (пересечения, статусы)
```

## Эндпоинты (25), префикс `/api/v1`

| Сущность | Маршруты |
|---|---|
| Специализации (5) | `POST`, `GET /specializations`; `GET`, `PATCH`, `DELETE /specializations/{specialization_id}` |
| Врачи (6) | `POST`, `GET /doctors`; `GET`, `PUT`, `PATCH`, `DELETE /doctors/{doctor_id}` |
| Пациенты (6) | `POST`, `GET /patients`; `GET`, `PUT`, `PATCH`, `DELETE /patients/{patient_id}` |
| Записи (8) | `POST`, `GET /appointments`; `GET`, `PATCH /appointments/{appointment_id}`; `PATCH .../cancel`; `PATCH .../complete`; `GET /doctors/{doctor_id}/appointments`; `GET /patients/{patient_id}/appointments` |

Фильтры:
- `GET /doctors`: `specialization_id`, `is_active`, `min_experience`, `max_price`, `search`
- `GET /patients`: `search`
- `GET /appointments`: `doctor_id`, `patient_id`, `status`, `date` (YYYY-MM-DD, день по UTC)

## Правила

- Время приёма передаётся с часовым поясом (`2026-12-01T10:00:00+05:00`) и хранится в UTC. Ответ содержит вычисляемое поле `end_at`.
- Длительность: 15, 30, 45 или 60 минут. Начало приёма должно быть в будущем.
- Записаться можно только к существующему и активному врачу.
- Записи пересекаются, если `new_start < existing_end AND existing_start < new_end`. Учитываются только записи `scheduled`; отменённые время не занимают.
- `PATCH /appointments/{id}` меняет `doctor_id`, `start_at`, `duration_minutes`, `reason` и заново проверяет занятость, не учитывая саму запись. Поле `status` в нём не принимается.
- Статусы: `scheduled → cancelled`, `scheduled → completed` (только после окончания приёма). Других переходов нет.
- Нельзя удалить специализацию, у которой есть врачи, а также врача или пациента, у которых есть хотя бы одна запись (любого статуса).
- ID после удаления повторно не выдаются.
- В схемах изменения неизвестные поля запрещены (`extra="forbid"`). `PATCH` меняет только переданные поля.

## Коды ответов

| Код | Когда |
|---|---|
| 200 | получение и изменение |
| 201 | создание |
| 204 | удаление |
| 404 | объект по ID (в том числе связанный) не найден |
| 409 | время занято, недопустимая смена статуса, неактивный врач, запрет удаления, дубль имени специализации или телефона пациента |
| 422 | ошибки валидации Pydantic (типы, ограничения, прошедшее время, лишние поля) |

## Пример

```bash
curl -X POST http://127.0.0.1:8000/api/v1/specializations \
  -H "Content-Type: application/json" \
  -d '{"name": "Кардиолог", "description": "Заболевания сердца и сосудов"}'
```
# hometaskk
