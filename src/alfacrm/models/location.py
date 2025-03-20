from typing import Optional
from pydantic import Field, field_validator
from .base import ALFABaseModel

class LocationBase(ALFABaseModel):
    """Базовые поля локации (опциональные для обновления)"""
    name: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Название локации"
    )
    is_active: Optional[int] = Field(
        default=None,
        ge=0, le=1,
        description="Статус активности: 0 - неактивно, 1 - активно"
    )
    branch_id: Optional[int] = Field(
        default=None,
        description="ID филиала (обязателен при создании)"
    )

    @field_validator("is_active")
    def validate_status(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError("Допустимые значения: 0 или 1")
        return v

class LocationCreate(LocationBase):
    """Обязательные поля для создания"""
    name: str = Field(..., max_length=50)
    is_active: int = Field(..., ge=0, le=1)
    branch_id: int = Field(...)

class LocationUpdate(LocationBase):
    """Поля для обновления (все опциональны)"""
    pass

class LocationResponse(LocationBase):
    """Поля ответа API (включая read-only)"""
    id: int = Field(..., description="Уникальный идентификатор")

class LocationFilter(ALFABaseModel):
    """Фильтрация и пагинация для метода index"""
    id: Optional[int] = None
    page: int = Field(default=0, ge=0, description="Номер страницы (с 0)")
