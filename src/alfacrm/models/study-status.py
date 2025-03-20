from typing import Optional
from pydantic import BaseModel, Field, field_validator
from .base import ALFABaseModel

class StudyStatusBase(ALFABaseModel):
    """Базовые поля статуса обучения"""
    name: Optional[str] = Field(
        None,
        max_length=50,
        description="Наименование статуса"
    )
    is_enabled: Optional[int] = Field(
        None,
        ge=0, le=1,
        description="Флаг активности (0 - выключен, 1 - включен)"
    )

    @field_validator("is_enabled")
    def validate_enabled_status(cls, v: int | None) -> int | None:
        if v is not None and v not in (0, 1):
            raise ValueError("Допустимые значения: 0 или 1")
        return v

class StudyStatusCreate(StudyStatusBase):
    """Обязательные поля для создания статуса"""
    name: str = Field(..., max_length=50)
    is_enabled: int = Field(...)

class StudyStatusUpdate(StudyStatusBase):
    """Поля для обновления"""
    pass

class StudyStatusResponse(StudyStatusBase):
    """Ответ API с идентификатором"""
    id: int = Field(..., description="Уникальный ID статуса")

class StudyStatusFilter(ALFABaseModel):
    """Фильтрация и пагинация для метода index"""
    id: Optional[int] = Field(
        None,
        description="Фильтр по ID статуса"
    )
    name: Optional[str] = Field(
        None,
        description="Фильтр по названию"
    )
    is_enabled: Optional[int] = Field(
        None,
        ge=0, le=1,
        description="Фильтр по активности"
    )
    page: int = Field(
        default=0,
        ge=0,
        description="Номер страницы (начиная с 0)"
    )
