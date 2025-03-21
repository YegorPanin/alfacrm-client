# task.py
from datetime import date, datetime
from typing import Optional, Literal
from pydantic import Field, model_validator, field_validator
from .base import ALFABaseModel, DateRangeMixin
import re

TaskStatus = Literal['new', 'in_progress', 'completed', 'canceled']
TaskPriority = Literal['low', 'medium', 'high']

class TaskBase(ALFABaseModel):
    """Базовые параметры задачи"""
    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Заголовок задачи"
    )
    description: Optional[str] = Field(None, max_length=1000)
    due_date: date = Field(..., description="Срок выполнения")
    status: TaskStatus = Field('new')
    priority: TaskPriority = Field('medium')
    type_id: int = Field(..., gt=0, description="Тип задачи из справочника")
    customer_id: Optional[int] = Field(None, gt=0)
    assigned_to: int = Field(..., gt=0, description="Исполнитель")
    branch_id: int = Field(..., gt=0)

    @field_validator("due_date", mode="before")
    def parse_due_date(cls, v: str | date) -> date:
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d").date()
        return v

    @model_validator(mode='after')
    def validate_due_date(self) -> 'TaskBase':
        if self.due_date < date.today():
            raise ValueError("Дата выполнения не может быть в прошлом")
        return self

class TaskCreate(TaskBase):
    """Обязательные поля при создании задачи"""
    pass

class TaskUpdate(ALFABaseModel):
    """Поля для обновления задачи"""
    status: Optional[TaskStatus] = None
    due_date: Optional[date] = None
    assigned_to: Optional[int] = Field(None, gt=0)
    description: Optional[str] = None

class TaskResponse(TaskBase):
    """Полные данные задачи из системы"""
    id: int = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    completed_at: Optional[datetime] = None

class TaskFilter(ALFABaseModel, DateRangeMixin):
    """Фильтр для поиска задач"""
    title: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    type_id: Optional[int] = None
    customer_id: Optional[int] = None
    assigned_to: Optional[int] = None
    show_completed: bool = Field(False, description="Включать выполненные")
    page: int = Field(0, ge=0)
