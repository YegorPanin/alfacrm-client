# teacher.py
from datetime import date, time
from typing import List, Optional, Literal
from pydantic import Field, model_validator, field_validator
from .base import ALFABaseModel, DateRangeMixin
import re


class TeacherRateBase(ALFABaseModel):
    """Базовые параметры ставки преподавателя"""
    subject_id: int = Field(..., gt=0, description="ID предмета")
    lesson_type_id: int = Field(..., gt=0, description="ID типа занятия")
    rate: float = Field(..., gt=0, description="Ставка за занятие")


class TeacherWorkingHours(ALFABaseModel):
    """График работы преподавателя"""
    day_of_week: int = Field(..., ge=1, le=7, description="День недели 1-ПН,7-ВС")
    time_from: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Начало работы (HH:MM)")
    time_to: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="Окончание работы (HH:MM)")

    @model_validator(mode='after')
    def validate_time_range(self) -> 'TeacherWorkingHours':
        start = list(map(int, self.time_from.split(":")))
        end = list(map(int, self.time_to.split(":")))

        if time(*start) >= time(*end):
            raise ValueError("Время начала должно быть раньше окончания")
        return self


class TeacherBase(ALFABaseModel):
    """Основные данные преподавателя"""
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    patronymic: Optional[str] = Field(None, min_length=2, max_length=50)
    phone: Optional[str] = Field(None, pattern=r"^\+7\d{10}$")
    email: Optional[str] = Field(None, pattern=r"^[^@]+@[^@]+\.[^@]+$")
    status: Literal['active', 'fired'] = Field('active')
    birth_date: Optional[date] = None
    subjects: List[int] = Field(default_factory=list, description="ID преподаваемых предметов")
    branch_id: int = Field(..., gt=0, description="ID филиала")

    @field_validator("phone")
    def validate_phone(cls, v: str) -> str:
        if v and not re.match(r"^\+7\d{10}$", v):
            raise ValueError("Неверный формат телефона. Пример: +74951234567")
        return v


class TeacherCreate(TeacherBase):
    """Создание нового преподавателя"""
    rates: Optional[List[TeacherRateBase]] = None
    working_hours: Optional[List[TeacherWorkingHours]] = None


class TeacherUpdate(ALFABaseModel):
    """Обновление данных преподавателя"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    status: Optional[Literal['active', 'fired']] = None
    phone: Optional[str] = Field(None, pattern=r"^\+7\d{10}$")
    email: Optional[str] = None
    subjects: Optional[List[int]] = None


class TeacherResponse(TeacherBase):
    """Полные данные преподавателя из системы"""
    id: int = Field(..., description="Уникальный идентификатор")
    created_at: date = Field(..., description="Дата создания записи")
    updated_at: date = Field(..., description="Дата обновления")
    rates: List[TeacherRateBase] = Field(default_factory=list)
    working_hours: List[TeacherWorkingHours] = Field(default_factory=list)


class TeacherFilter(ALFABaseModel, DateRangeMixin):
    """Фильтр для поиска преподавателей"""
    name: Optional[str] = Field(None, description="Поиск по ФИО")
    status: Optional[Literal['active', 'fired']] = None
    subject_id: Optional[int] = Field(None, gt=0)
    branch_id: Optional[int] = Field(None, gt=0)
    has_working_hours: Optional[bool] = Field(
        None,
        description="Фильтр по наличию графика работы"
    )
    page: int = Field(0, ge=0)
