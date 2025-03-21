from typing import Optional
from pydantic import Field, field_validator
from .base import ALFABaseModel

class LeadSourceBase(ALFABaseModel):
    """Базовые поля источника лидов"""
    code: Optional[str] = Field(
        None,
        max_length=50,
        description="Уникальный код (латиница/цифры)"
    )
    name: Optional[str] = Field(
        None,
        max_length=50,
        description="Название источника"
    )
    is_enabled: Optional[int] = Field(
        None,
        ge=0, 
        le=1,
        description="Статус активности (0-неактивен, 1-активен)"
    )

    @field_validator("code", "name")
    def validate_length(cls, v: str) -> str:
        if v and len(v) > 50:
            raise ValueError("Максимальная длина - 50 символов")
        return v

    @field_validator("is_enabled")
    def validate_bool(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError("Допустимые значения: 0 или 1")
        return v

class LeadSourceCreate(LeadSourceBase):
    """Обязательные поля при создании"""
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=50)
    is_enabled: int = Field(...)

class LeadSourceUpdate(LeadSourceBase):
    """Поля для обновления (все опциональны)"""
    pass

class LeadSourceResponse(LeadSourceBase):
    """Ответ API с ID источника"""
    id: int = Field(..., description="Уникальный идентификатор")

class LeadSourceFilter(ALFABaseModel):
    """Фильтрация и пагинация"""
    id: Optional[int] = None
    code: Optional[str] = None
    name: Optional[str] = None
    is_enabled: Optional[int] = Field(None, ge=0, le=1)
    page: int = Field(0, ge=0)
