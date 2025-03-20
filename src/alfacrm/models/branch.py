from typing import Optional, List
from pydantic import Field, field_validator
from .base import ALFABaseModel


class BranchBase(ALFABaseModel):
    """Базовая модель с опциональными полями."""
    name: Optional[str] = Field(
        default=None, 
        max_length=50, 
        description="Название филиала"
    )
    is_active: Optional[int] = Field(
        default=None, 
        ge=0, le=1, 
        description="0 - неактивен, 1 - активен"
    )
    subject_ids: Optional[List[int]] = Field(
        default=None,
        description="ID связанных предметов"
    )

    @field_validator("is_active")
    def validate_is_active(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError("Допустимые значения: 0 или 1")
        return v


class BranchCreate(BranchBase):
    """Модель для создания филиала."""
    name: str = Field(..., max_length=50, description="Название филиала")
    is_active: int = Field(..., ge=0, le=1, description="0 - неактивен, 1 - активен")


class BranchUpdate(BranchBase):
    """Модель для обновления филиала."""
    pass
