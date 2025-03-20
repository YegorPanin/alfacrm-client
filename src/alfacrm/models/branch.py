from typing import Optional, List
from pydantic import Field, field_validator
from .base import ALFABaseModel

class BranchBase(ALFABaseModel):
    """Базовая модель с общими полями (все опциональные)"""
    name: Optional[str] = Field(None, max_length=50, description="Наименование")
    is_active: Optional[int] = Field(None, ge=0, le=1, description="Флаг активности")
    subject_ids: Optional[List[int]] = Field(None, description="Массив ID предметов")

class BranchCreate(BranchBase):
    """Модель создания: name обязателен, остальное наследуется"""
    name: str = Field(..., max_length=50, description="Наименование")

class BranchUpdate(BranchBase):
    """Модель обновления: все поля опциональны"""
    pass

class BranchFilter(BranchBase):
    """Модель фильтрации: добавляем id"""
    id: Optional[int] = Field(None, description="ID филиала")
