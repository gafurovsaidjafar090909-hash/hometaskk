from fastapi import FastAPI

from routers import appointments, doctors, patients, specializations

app = FastAPI(
    title="MedBook API",
    description="Учебный API онлайн-записи к врачам. Данные хранятся в памяти и теряются после перезапуска.",
    version="1.0.0",
)

for module in (specializations, doctors, patients, appointments):
    app.include_router(module.router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
def root():
    return {"message": "MedBook API работает", "docs": "/docs"}
