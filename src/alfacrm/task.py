from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
import re

class TaskBase(BaseModel):
    """Базовые поля задачи"""
    company_id: Optional[int] = Field(None, description="ID компании")
    user_id: Optional[int] = Field(None, description="ID создателя")
    assigned_ids: Optional[List[int]] = Field(None, description="ID исполнителей")
    group_ids: Optional[List[int]] = Field(None, description="ID групп")
    customer_ids: Optional[List[int]] = Field(None, description="ID клиентов")
    title: Optional[str] = Field(None, max_length=255, description="Заголовок")
    text: Optional[str] = Field(None, description="Описание задачи")
    is_archive: Optional[bool] = Field(None, description="Архивная")
    is_done: Optional[bool] = Field(None, description="Выполнена")
    is_private: Optional[bool] = Field(None, description="Приватная")
    due_date: Optional[str] = Field(None, description="Дедлайн (YYYY-MM-DD)")
    done_date: Optional[str] = Field(None, description="Дата выполнения")
    priority: Optional[Literal[1, 2, 3]] = Field(
        None, 
        description="1-низкий, 2-нормальный, 3-высокий"
    )

    @field_validator("due_date", "done_date", "created_at")
    def validate_dates(cls, v: str) -> str:
        if v and not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Формат даты: YYYY-MM-DD")
        return v

class TaskCreate(TaskBase):
    """Обязательные поля для создания задачи"""
    title: str = Field(..., max_length=255)
    text: str = Field(...)
    user_id: int = Field(...)
    assigned_ids: List[int] = Field(..., min_items=1)

class TaskUpdate(BaseModel):
    """Поля для обновления задачи"""
    note: Optional[str] = Field(None, max_length=500, description="Комментарий")

class TaskResponse(TaskBase):
    """Полный ответ API"""
    id: int
    created_at: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    updated_at: Optional[str] = None

class TaskFilter(BaseModel):
    """Фильтрация задач"""
    id: Optional[int] = None
    user_id: Optional[int] = None
    assigned_id: Optional[int] = None
    text: Optional[str] = None
    priority: Optional[Literal[1, 2, 3]] = None
    due_date_from: Optional[str] = None
    due_date_to: Optional[str] = None
    due_date_is_null: Optional[bool] = None
    done_date_from: Optional[str] = None
    done_date_to: Optional[str] = None
    is_done: Optional[bool] = None
    is_archive: Optional[bool] = None
    page: int = Field(0, ge=0)

    @field_validator("due_date_from", "due_date_to", "done_date_from", "done_date_to")
    def validate_date_format(cls, v: str) -> str:
        if v and not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Формат даты: YYYY-MM-DD")
        return v

    @model_validator(mode="after")
    def validate_date_ranges(self) -> 'TaskFilter':
        if self.due_date_from and self.due_date_to:
            if self.due_date_from > self.due_date_to:
                raise ValueError("due_date_to должен быть >= due_date_from")
        
        if self.done_date_from and self.done_date_to:
            if self.done_date_from > self.done_date_to:
                raise ValueError("done_date_to должен быть >= done_date_from")
        
        return self
