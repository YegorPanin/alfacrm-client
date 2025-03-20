from typing import Optional, List
from pydantic import Field, field_validator, model_validator
import re
from .base import ALFABaseModel

class GroupBase(ALFABaseModel):
    """Базовые поля группы (опциональные для обновления)"""
    name: Optional[str] = Field(
        None, 
        max_length=50, 
        description="Название группы"
    )
    branch_ids: Optional[List[int]] = Field(
        None, 
        description="ID привязанных филиалов"
    )
    teacher_ids: Optional[List[int]] = Field(
        None, 
        description="ID ответственных педагогов"
    )
    level_id: Optional[int] = Field(
        None, 
        description="ID уровня группы"
    )
    status_id: Optional[int] = Field(
        None, 
        description="ID статуса группы"
    )
    b_date: Optional[str] = Field(
        None, 
        description="Дата начала действия (YYYY-MM-DD)"
    )
    e_date: Optional[str] = Field(
        None, 
        description="Дата окончания действия (YYYY-MM-DD)"
    )
    note: Optional[str] = Field(
        None,
        max_length=255, 
        description="Комментарий"
    )

    @field_validator("b_date", "e_date")
    def validate_dates(cls, v: str) -> str:
        if v and not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Некорректный формат даты. Используйте YYYY-MM-DD")
        return v

class GroupCreate(GroupBase):
    """Обязательные поля для создания группы"""
    name: str = Field(..., max_length=50)
    branch_ids: List[int] = Field(..., min_length=1)

class GroupUpdate(GroupBase):
    """Все поля опциональны для частичного обновления"""
    pass

class GroupResponse(GroupBase):
    """Поля ответа API с read-only данными"""
    id: int = Field(..., description="Уникальный идентификатор")
    updated_at: Optional[str] = Field(
        None, 
        description="Дата обновления (DD.MM.YYYY)"
    )
    created_at: Optional[str] = Field(
        None, 
        description="Дата создания (DD.MM.YYYY)"
    )

class GroupFilter(ALFABaseModel):
    """Модель для фильтрации групп с валидацией"""
    # Основные параметры
    ids: Optional[List[int]] = None
    id: Optional[int] = None
    name: Optional[str] = None
    note: Optional[str] = None
    customer_name: Optional[str] = None
    removed: Optional[int] = Field(
        None, 
        ge=0, 
        le=2, 
        description="0-активные, 1-все, 2-архивные"
    )
    
    # Фильтры по связям
    level_id: Optional[int] = None
    status_id: Optional[int] = None
    branch_id: Optional[int] = None
    teacher_id: Optional[int] = None
    
    # Диапазоны дат
    b_date_from: Optional[str] = None
    b_date_to: Optional[str] = None
    e_date_from: Optional[str] = None
    e_date_to: Optional[str] = None
    
    # Форматированные даты
    updated_at_from: Optional[str] = None
    updated_at_to: Optional[str] = None
    created_at_from: Optional[str] = None
    created_at_to: Optional[str] = None
    
    # Пагинация
    page: int = Field(0, ge=0)

    @field_validator(
        "b_date_from", "b_date_to", 
        "e_date_from", "e_date_to"
    )
    def validate_iso_format(cls, v: str) -> str:
        if v and not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Формат даты: YYYY-MM-DD")
        return v

    @field_validator(
        "updated_at_from", "updated_at_to",
        "created_at_from", "created_at_to"
    )
    def validate_dot_format(cls, v: str) -> str:
        if v and not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
            raise ValueError("Формат даты: DD.MM.YYYY")
        return v

    @model_validator(mode="after")
    def check_dates(self) -> "GroupFilter":
        # Валидация корректности диапазонов
        date_pairs = [
            ("b_date_from", "b_date_to"),
            ("e_date_from", "e_date_to"),
            ("updated_at_from", "updated_at_to"),
            ("created_at_from", "created_at_to")
        ]
        
        for start, end in date_pairs:
            start_val = getattr(self, start)
            end_val = getattr(self, end)
            if start_val and end_val and start_val > end_val:
                raise ValueError(f"{end} должна быть больше {start}")
        
        return self
