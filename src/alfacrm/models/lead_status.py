from typing import Optional
from pydantic import BaseModel, Field, field_validator
from .base import ALFABaseModel

class LeadStatusBase(ALFABaseModel):
    """Базовые поля этапа воронки"""
    name: Optional[str] = Field(
        None,
        max_length=50,
        description="Название этапа"
    )
    is_enabled: Optional[int] = Field(
        None,
        ge=0, le=1,
        description="Активность (0-нет, 1-да)"
    )

    @field_validator("is_enabled")
    def validate_enabled(cls, v: int | None) -> int | None:
        if v is not None and v not in (0, 1):
            raise ValueError("Допустимые значения: 0 или 1")
        return v

class LeadStatusCreate(LeadStatusBase):
    """Создание этапа (обязательные поля)"""
    name: str = Field(..., max_length=50)
    is_enabled: int = Field(...)

class LeadStatusUpdate(LeadStatusBase):
    """Обновление этапа (все поля опциональны)"""
    pass

class LeadStatusResponse(LeadStatusBase):
    """Ответ с ID этапа"""
    id: int = Field(..., description="Уникальный идентификатор")

class LeadStatusFilter(ALFABaseModel):
    """Фильтрация для метода index"""
    id: Optional[int] = None
    name: Optional[str] = None
    is_enabled: Optional[int] = Field(None, ge=0, le=1)
    page: int = Field(0, ge=0)
