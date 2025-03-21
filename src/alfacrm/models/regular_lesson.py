from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
import re

class RegularLessonBase(BaseModel):
    """Базовые поля регулярного урока"""
    lesson_type_id: Optional[int] = Field(None, description="Тип урока")
    related_class: Optional[Literal["Group", "Customer"]] = None
    related_id: Optional[int] = Field(None, description="ID группы/клиента")
    subject_id: Optional[int] = Field(None, description="ID предмета")
    teacher_ids: Optional[List[int]] = Field(None, min_items=1, description="ID преподавателей")
    room_id: Optional[int] = Field(None, description="ID аудитории")
    day: Optional[str] = Field(None, pattern=r"^[1-7]$", description="День недели (1-7)")
    days: Optional[str] = Field(None, max_length=20, description="Расписание дней")
    time_from_v: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$", description="Начало (HH:MM)")
    time_to_v: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$", description="Окончание (HH:MM)")
    b_date: Optional[str] = Field(None, description="Начало периода (DD.MM.YYYY)")
    e_date: Optional[str] = Field(None, description="Конец периода (DD.MM.YYYY)")

class RegularLessonCreate(RegularLessonBase):
    """Обязательные поля для создания урока"""
    lesson_type_id: int = Field(...)
    related_class: Literal["Group", "Customer"] = Field(...)
    related_id: int = Field(...)
    subject_id: int = Field(...)
    teacher_ids: List[int] = Field(..., min_items=1)
    time_from_v: str = Field(...)
    time_to_v: str = Field(...)
    b_date: str = Field(...)
    e_date: str = Field(...)

    @field_validator("b_date", "e_date")
    def validate_dates(cls, v: str) -> str:
        if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
            raise ValueError("Формат даты: DD.MM.YYYY")
        return v

class RegularLessonUpdate(BaseModel):
    """Поля для обновления урока"""
    note: Optional[str] = Field(None, max_length=500, description="Примечание")

class RegularLessonResponse(RegularLessonBase):
    """Полная модель ответа"""
    id: int
    branch_id: int
    updated_at: datetime
    created_at: datetime

class RegularLessonFilter(BaseModel):
    """Фильтрация регулярных уроков"""
    ids: Optional[List[int]] = None
    id: Optional[int] = None
    subject_id: Optional[int] = None
    teacher_id: Optional[int] = None
    date_from: Optional[str] = None  # DD.MM.YYYY
    date_to: Optional[str] = None
    time_from: Optional[str] = None  # YYYY-MM-DD HH:MM:SS
    time_to: Optional[str] = None
    public: Optional[Literal[0, 1]] = None
    page: int = Field(0, ge=0)

    @field_validator("date_from", "date_to")
    def validate_dates(cls, v: str) -> str:
        if v and not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
            raise ValueError("Некорректный формат даты. Используйте DD.MM.YYYY")
        return v

    @field_validator("time_from", "time_to")
    def validate_times(cls, v: str) -> str:
        if v:
            try:
                datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError("Формат времени: YYYY-MM-DD HH:MM:SS")
        return v

    @model_validator(mode="after")
    def validate_periods(cls, values):
        if values.date_from and values.date_to and values.date_from > values.date_to:
            raise ValueError("date_to должен быть позже date_from")
        if values.time_from and values.time_to and values.time_from > values.time_to:
            raise ValueError("time_to должен быть позже time_from")
        return values
