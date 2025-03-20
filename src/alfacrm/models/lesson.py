from datetime import time
from typing import Optional, List, Annotated
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
import re

class LessonDetailBase(BaseModel):
    """Базовый класс для деталей урока"""
    customer_id: int = Field(..., description="ID клиента")
    ctt_id: Optional[int] = Field(None, description="ID абонемента")
    is_attend: Optional[bool] = Field(None, description="Присутствие (1-да, 0-нет)")
    reason_id: Optional[int] = Field(None, description="ID причины отсутствия")
    commission: Optional[float] = Field(None, ge=0)
    grade: Optional[float] = Field(None, ge=0, le=5)
    homework_grade_id: Optional[int] = None
    bonus: Optional[float] = None
    note: Optional[str] = None

    @model_validator(mode="after")
    def check_attendance(self) -> 'LessonDetailBase':
        if self.is_attend == 0 and self.reason_id is None:
            raise ValueError("При отсутствии требуется reason_id")
        return self

class LessonDetailCreate(LessonDetailBase):
    """Детали при проведении урока (обязательные поля)"""
    id: int = Field(..., description="ID детали урока")
    branch_id: int = Field(..., description="ID филиала")
    lesson_id: int = Field(..., description="ID урока")

class LessonBase(BaseModel):
    """Общие поля для урока (все опциональны для обновления)"""
    branch_id: Optional[int] = None
    teacher_ids: Optional[List[int]] = None
    customer_ids: Optional[List[int]] = None
    group_ids: Optional[List[int]] = None
    lesson_type_id: Optional[int] = None
    subject_id: Optional[int] = None
    room_id: Optional[int] = None
    status: Optional[int] = Field(
        default=3, 
        ge=1, 
        le=3, 
        description="1-запланирован, 2-отменен, 3-проведен (default)"
    )
    topic: Optional[str] = None
    note: Optional[str] = None
    homework: Optional[str] = None

class LessonCreate(LessonBase):
    """Обязательные поля для создания урока"""
    lesson_date: str = Field(..., description="Дата (DD.MM.YYYY)")
    time_from: str = Field(..., description="Время начала (HH:MM)")
    duration: int = Field(..., gt=0, description="Длительность в минутах")
    lesson_type_id: int = Field(...)
    subject_id: int = Field(...)

    @field_validator("lesson_date")
    def validate_lesson_date(cls, v: str) -> str:
        if not re.match(r"\d{2}\.\d{2}\.\d{4}", v):
            raise ValueError("Формат даты: DD.MM.YYYY")
        return v

    @field_validator("time_from")
    def validate_time_format(cls, v: str) -> str:
        if not re.match(r"^\d{2}:\d{2}$", v):
            raise ValueError("Формат времени: HH:MM")
        return v

class LessonUpdate(LessonBase):
    """Поля для обновления урока"""
    pass

class LessonResponse(LessonBase):
    """Полная модель урока с read-only полями"""
    id: int = Field(...)
    date: str = Field(..., description="Дата урока (YYYY-MM-DD)")
    time_from: str = Field(..., description="Начало (HH:MM:SS)")
    time_to: str = Field(..., description="Окончание (HH:MM:SS)")
    regular_id: Optional[int] = None
    details: List[LessonDetailBase] = []
    updated_at: Optional[str] = Field(None, pattern=r"\d{2}\.\d{2}\.\d{4}")
    created_at: Optional[str] = Field(None, pattern=r"\d{2}\.\d{2}\.\d{4}")
    
class LessonTeachRequest(BaseModel):
    """Модель для проведения урока (метод teach)"""
    id: int = Field(..., description="ID запланированного урока")
    time_from: str = Field(..., description="Фактическое время начала (HH:MM:SS)")
    time_to: str = Field(..., description="Фактическое время окончания")
    status: int = Field(3, ge=1, le=3)
    details: List[LessonDetailCreate] = Field(..., min_length=1)
    topic: Optional[str] = None
    homework: Optional[str] = None

    @model_validator(mode="after")
    def validate_lesson_type(self) -> 'LessonTeachRequest':
        if self.status != 3:
            raise ValueError("Статус должен быть 3 (проведен) для данного метода")
        return self

class LessonFilter(BaseModel):
    """Фильтрация уроков с пагинацией"""
    id: Optional[int] = None
    status: int = Field(3, ge=1, le=3)
    teacher_id: Optional[int] = None
    customer_id: Optional[int] = None
    group_id: Optional[int] = None
    date_from: Optional[str] = Field(None, pattern=r"\d{4}-\d{2}-\d{2}")
    date_to: Optional[str] = Field(None, pattern=r"\d{4}-\d{2}-\d{2}")
    page: int = Field(0, ge=0)
