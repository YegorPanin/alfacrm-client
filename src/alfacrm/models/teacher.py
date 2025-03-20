from datetime import date
from typing import Optional, List, Literal, Annotated
from pydantic import (
    BaseModel, 
    Field, 
    field_validator, 
    model_validator, 
    conint, 
    conlist,
    ConfigDict
)
import re

# ================== TEACHER ==================
class TeacherBase(BaseModel):
    """Базовые поля педагога"""
    branch_ids: Optional[List[int]] = Field(None, min_length=1)
    name: Optional[str] = Field(None, max_length=100, pattern=r"^[а-яА-Я\s\-]+$")
    dob: Optional[str] = Field(None, description="Дата рождения (DD.MM.YYYY)")
    gender: Optional[Literal[0, 1]] = Field(None, description="0-жен, 1-муж")
    subject_id: Optional[int] = Field(None, description="Основной предмет")
    skill_id: Optional[int] = None
    note: Optional[str] = Field(None, max_length=500)

    @field_validator("dob")
    def validate_dob(cls, v: str) -> str:
        if v and not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
            raise ValueError("Неверный формат даты (DD.MM.YYYY)")
        return v

class TeacherCreate(TeacherBase):
    """Обязательные поля для создания"""
    name: str = Field(..., max_length=100)
    branch_ids: List[int] = Field(..., min_length=1)

class TeacherUpdate(BaseModel):
    """Поля для обновления"""
    note: Optional[str] = Field(None, max_length=500)

class TeacherResponse(TeacherBase):
    """Ответ API с системными полями"""
    id: int
    subject_name: Optional[str] = None
    skill_name: Optional[str] = None
    e_date: Optional[str] = Field(None, pattern=r"^\d{2}\.\d{2}\.\d{4}$")
    created_at: date

class TeacherFilter(BaseModel):
    """Фильтрация педагогов"""
    name: Optional[str] = None
    phone: Optional[str] = None
    removed: Optional[Literal[0, 1, 2]] = Field(
        None, 
        description="0-активные, 1-все, 2-архив"
    )
    age_from: Optional[conint(ge=18, le=100)] = None
    age_to: Optional[conint(ge=18, le=100)] = None
    subject_id: Optional[int] = None
    skill_id: Optional[int] = None
    branch_id: Optional[int] = None
    e_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    page: int = Field(0, ge=0)

    @model_validator(mode="after")
    def validate_age_range(self) -> 'TeacherFilter':
        if self.age_from and self.age_to and self.age_from > self.age_to:
            raise ValueError("age_to должен быть >= age_from")
        return self

# ================== WORKING HOUR ==================
class WorkingHourBase(BaseModel):
    """График работы педагога"""
    location_id: Optional[int] = None
    weekday: Optional[conint(ge=1, le=7)] = Field(
        None,
        description="1-ВС, 7-СБ"
    )
    time_from: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}:\d{2}$")
    time_to: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}:\d{2}$")

class WorkingHourCreate(WorkingHourBase):
    """Создание графика"""
    teacher_id: int = Field(...)
    time_from: str = Field(...)
    time_to: str = Field(...)

class WorkingHourResponse(WorkingHourBase):
    """Ответ API"""
    id: int
    teacher_id: int

class WorkingHourFilter(BaseModel):
    """Фильтрация графиков"""
    id: Optional[int] = None
    location_id: Optional[int] = None
    weekday: Optional[int] = None
    time_from: Optional[str] = None
    time_to: Optional[str] = None
    teacher_id: Optional[int] = None
    page: int = Field(0, ge=0)

# ================== TEACHER RATE ==================
class TeacherRateCondition(Literal[1, 2, 3]):
    """Условия начисления ставки"""
    ATTENDED = 1
    MISSED = 2
    ANY = 3

class TeacherRateBase(BaseModel):
    """Ставки педагога"""
    rate: Optional[float] = Field(None, ge=0)
    type: Optional[Literal[1, 2]] = Field(
        None,
        description="1-фикс, 2-процент"
    )
    b_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    e_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    s_multirate: Optional[bool] = None
    is_proportional: Optional[bool] = None
    condition_attend: Optional[TeacherRateCondition] = None
    reason_ids: Optional[List[int]] = None
    count_from: Optional[conint(ge=1)] = None
    count_to: Optional[conint(ge=1)] = None
    duration: Optional[conint(ge=15)] = None
    lesson_type_ids: Optional[List[int]] = None
    subject_ids: Optional[List[int]] = None
    is_gt_zero: Optional[bool] = None

class TeacherRateCreate(TeacherRateBase):
    """Создание ставки"""
    teacher_id: int = Field(...)
    rate: float = Field(..., ge=0)
    type: Literal[1, 2] = Field(...)

class TeacherRateResponse(TeacherRateBase):
    """Ответ API"""
    id: int
    teacher_id: int

class TeacherRateFilter(BaseModel):
    """Фильтрация ставок"""
    id: Optional[int] = None
    teacher_id: Optional[int] = None
    type: Optional[Literal[1, 2]] = None
    b_date_from: Optional[str] = None
    b_date_to: Optional[str] = None
    e_date_from: Optional[str] = None
    e_date_to: Optional[str] = None
    lesson_type_ids: Optional[List[int]] = None
    subject_ids: Optional[List[int]] = None
    page: int = Field(0, ge=0)

    @model_validator(mode="after")
    def validate_dates(cls, values):
        date_fields = [
            ('b_date_from', 'b_date_to'),
            ('e_date_from', 'e_date_to')
        ]
        
        for start, end in date_fields:
            if getattr(values, start) and getattr(values, end):
                if getattr(values, start) > getattr(values, end):
                    raise ValueError(f"{end} должен быть >= {start}")
        return values
