from typing import Optional
from pydantic import Field, field_validator
from .base import ALFABaseModel

class LeadRejectBase(ALFABaseModel):
    """Базовые поля модели"""
    name: Optional[str] = Field(
        None, 
        max_length=50, 
        description="Название причины отказа"
    )
    is_enabled: Optional[int] = Field(
        None, 
        description="0 - отключена, 1 - активна",
        ge=0, 
        le=1
    )
    weight: Optional[int] = Field(
        None, 
        description="Порядок сортировки",
        ge=0
    )

    @field_validator("is_enabled")
    def validate_enabled(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError("Допустимые значения: 0 или 1")
        return v

class LeadRejectCreate(LeadRejectBase):
    """Обязательные поля при создании"""
    name: str = Field(..., max_length=50)
    is_enabled: int = Field(...)

class LeadRejectUpdate(LeadRejectBase):
    """Все поля опциональны для изменения"""
    pass

class LeadRejectResponse(LeadRejectBase):
    """Read-only поля, возвращаемые API"""
    id: int = Field(..., description="Уникальный идентификатор")

class LeadRejectFilter(ALFABaseModel):
    """Фильтрация и пагинация для метода index"""
    page: int = Field(
        default=0, 
        ge=0, 
        description="Номер страницы (начинается с 0)"
    )
