from typing import Optional
from pydantic import Field, field_validator
from .base import ALFABaseModel

class RoomBase(ALFABaseModel):
    """Базовые поля аудитории (все опциональны)"""
    branch_id: Optional[int] = Field(
        None, 
        description="ID филиала (обязателен при создании)"
    )
    location_id: Optional[int] = Field(
        None, 
        description="ID локации (Location)"
    )
    streaming_id: Optional[int] = Field(
        None, 
        description="ID стрима в платформе"
    )
    color_id: Optional[int] = Field(
        None, 
        description="Идентификатор цвета в календаре"
    )
    name: Optional[str] = Field(
        None, 
        max_length=50, 
        description="Короткое название аудитории"
    )
    note: Optional[str] = Field(
        None, 
        max_length=50, 
        description="Полное название"
    )
    is_enabled: Optional[int] = Field(
        None, 
        ge=0, le=1, 
        description="1 - активна, 0 - отключена"
    )
    weight: Optional[int] = Field(
        None, 
        ge=0, 
        description="Значение для сортировки"
    )

    @field_validator("is_enabled")
    def validate_enabled_status(cls, v: int | None) -> int | None:
        if v is not None and v not in (0, 1):
            raise ValueError("Допустимы только значения 0 или 1")
        return v

class RoomCreate(RoomBase):
    """Обязательные поля для создания аудитории"""
    branch_id: int = Field(...)
    name: str = Field(..., max_length=50)
    color_id: int = Field(...)
    weight: int = Field(..., ge=0)

class RoomUpdate(RoomBase):
    """Поля для обновления (все опциональны)"""
    pass

class RoomResponse(RoomBase):
    """Ответ API с идентификатором и read-only полями"""
    id: int = Field(..., description="Уникальный ID")

class RoomFilter(ALFABaseModel):
    """Фильтр для метода index"""
    is_enabled: Optional[int] = Field(
        None, 
        ge=0, le=1, 
        description="Фильтр по статусу активности"
    )
    page: int = Field(
        default=0, 
        ge=0,
        description="Номер страницы (отсчет с 0)"
    )
