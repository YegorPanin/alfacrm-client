# lesson.py
from datetime import date, time
from typing import List, Optional, Union, Literal
from pydantic import Field, model_validator, field_validator
from .base import ALFABaseModel
import re


class LessonDetails(ALFABaseModel):
    """Детали проведенного урока"""
    id: int = Field(..., description="ID детали урока")
    customer_id: int = Field(..., description="ID клиента")
    is_attend: bool = Field(..., description="Присутствие клиента (True/False)")
    reason_id: Optional[int] = Field(None, description="ID причины отсутствия")
    grade: Optional[float] = Field(None, ge=0, le=100, description="Оценка за урок")
    homework_grade_id: Optional[int] = Field(None, description="ID оценки ДЗ")
    bonus: Optional[float] = Field(None, ge=0, description="Начисленные бонусы")
    note: Optional[str] = Field(None, max_length=500, description="Комментарий")


class LessonBase(ALFABaseModel):
    """Базовые поля урока"""
    subject_id: int = Field(..., gt=0, description="ID предмета")
    teacher_ids: List[int] = Field(
        default_factory=list,
        min_length=1,
        description="Список ID преподавателей"
    )
    room_id: Optional[int] = Field(None, gt=0, description="ID аудитории")
    status: Optional[Literal[1, 2, 3]] = Field(
        None,
        description="Статус: 1-запланирован, 2-отменен, 3-проведен"
    )
    topic: Optional[str] = Field(None, max_length=255, description="Тема урока")
    homework: Optional[str] = Field(None, description="Домашнее задание")
    duration: Optional[int] = Field(
        None,
        gt=0,
        description="Длительность в минутах"
    )


class LessonFilter(ALFABaseModel):
    """Фильтр для поиска уроков"""
    id: Optional[int] = Field(None, gt=0)
    status: Optional[Literal[1, 2, 3]] = None
    teacher_id: Optional[int] = Field(None, gt=0)
    customer_id: Optional[int] = Field(None, gt=0)
    group_id: Optional[int] = Field(None, gt=0)
    subject_id: Optional[int] = Field(None, gt=0)
    location_ids: Optional[List[int]] = None
    room_ids: Optional[List[int]] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = Field(0, ge=0)

    @model_validator(mode='after')
    def validate_dates(self) -> 'LessonFilter':
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("Дата начала не может быть позже даты окончания")
        return self

    @field_validator("date_from", "date_to", mode='before')
    def parse_date(cls, v: Union[str, date]) -> date:
        if isinstance(v, str):
            if not re.match(r"\d{4}-\d{2}-\d{2}", v):
                raise ValueError("Формат даты: YYYY-MM-DD")
            return date.fromisoformat(v)
        return v


class LessonCreate(LessonBase):
    """Обязательные поля для создания урока"""
    lesson_date: date = Field(..., description="Дата урока (YYYY-MM-DD)")
    time_from: str = Field(
        ...,
        pattern=r"^\d{2}:\d{2}$",
        description="Время начала (HH:MM)"
    )
    time_to: str = Field(
        ...,
        pattern=r"^\d{2}:\d{2}$",
        description="Время окончания (HH:MM)"
    )
    lesson_type_id: int = Field(..., gt=0, description="ID типа урока")
    group_ids: Optional[List[int]] = Field(
        None,
        description="ID групп (для групповых занятий)"
    )
    customer_ids: Optional[List[int]] = Field(
        None,
        description="ID клиентов (для индивидуальных занятий)"
    )

    @model_validator(mode='after')
    def validate_time_range(self) -> 'LessonCreate':
        start = list(map(int, self.time_from.split(":")))
        end = list(map(int, self.time_to.split(":")))

        start_min = start[0] * 60 + start[1]
        end_min = end[0] * 60 + end[1]

        if start_min >= end_min:
            raise ValueError("Время начала должно быть раньше времени окончания")
        return self


class LessonUpdate(LessonBase):
    """Поля для обновления урока"""
    lesson_date: Optional[date] = None
    time_from: Optional[str] = None
    time_to: Optional[str] = None
    status: Optional[Literal[1, 2, 3]] = None


class LessonTeachRequest(ALFABaseModel):
    """Модель для проведения урока"""
    id: int = Field(..., description="ID урока")
    teacher_ids: List[int] = Field(..., min_items=1)
    time_from: str
    time_to: str
    room_id: int
    status: Literal[3] = Field(3, description="Меняется статус на 'проведен'")
    details: List[LessonDetails]
    topic: Optional[str] = None
    homework: Optional[str] = None


class LessonResponse(LessonBase):
    """Полная модель урока для ответа API"""
    id: int
    branch_id: int
    regular_id: Optional[int]
    lesson_date: date
    time_from: time
    time_to: time
    created_at: str
    updated_at: str
    details: List[LessonDetails]
    custom_fields: Optional[dict] = None
