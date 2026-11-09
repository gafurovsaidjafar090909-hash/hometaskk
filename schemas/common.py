from typing import ClassVar
from pydantic import BaseModel, ConfigDict, model_validator


class InputSchema(BaseModel):
    """Базовая схема для входных данных: неизвестные поля запрещены."""
    model_config = ConfigDict(extra="forbid")


class UpdateSchema(InputSchema):
    """Базовая схема для PATCH: все поля необязательные, но null разрешён только в NULLABLE."""
    NULLABLE: ClassVar[set[str]] = set()

    @model_validator(mode="after")
    def check_nulls(self):
        bad = [f for f in self.model_fields_set if getattr(self, f) is None and f not in self.NULLABLE]
        if bad:
            raise ValueError(f"Поля не могут быть null: {', '.join(sorted(bad))}")
        return self
