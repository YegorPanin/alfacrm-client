from datetime import date
from typing import Optional, List
from pydantic import Field, field_validator, ConfigDict, model_validator
import re
from .base import ALFABaseModel

class CustomerBase(ALFABaseModel):
    """Базовые поля для создания/обновления клиента"""
    name: Optional[str] = Field(None, max_length=50, description="Полное имя")
    branch_ids: Optional[List[int]] = Field(None, description="ID филиалов")
    teacher_ids: Optional[List[int]] = Field(None, description="ID педагогов")
    legal_type: Optional[int] = Field(None, ge=1, le=2, description="1-физ.лицо, 2-юр.лицо")
    is_study: Optional[int] = Field(None, ge=0, le=1, description="0-лид, 1-клиент")
    study_status_id: Optional[int] = Field(None, description="ID статуса обучения")
    lead_source_id: Optional[int] = Field(None, description="ID источника")
    assigned_id: Optional[int] = Field(None, description="ID ответственного менеджера")
    employee_id: Optional[int] = Field(None, description="ID ответственного педагога")
    company_id: Optional[int] = Field(None, description="ID компании")
    legal_name: Optional[str] = Field(None, max_length=50, description="Имя заказчика")
    dob: Optional[date] = Field(None, description="Дата рождения")
    phone: Optional[List[str]] = Field(None, description="Телефоны")
    email: Optional[List[str]] = Field(None, description="Email адреса")
    web: Optional[List[str]] = Field(None, description="Сайты")
    addr: Optional[List[str]] = Field(None, description="Адреса")
    color: Optional[int] = Field(None, description="ID цвета")
    note: Optional[str] = Field(None, description="Примечание")

    @field_validator('legal_type')
    def validate_legal_type(cls, v: int) -> int:
        if v not in (1, 2):
            raise ValueError("legal_type может быть 1 или 2")
        return v

    @field_validator('is_study')
    def validate_is_study(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError("is_study может быть 0 или 1")
        return v

class CustomerCreate(CustomerBase):
    """Обязательные поля для создания клиента"""
    name: str = Field(..., max_length=50)
    legal_type: int = Field(...)
    is_study: int = Field(...)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Иванов Иван",
                "legal_type": 1,
                "is_study": 0,
                "phone": ["+79991234567"]
            }
        }
    )

class CustomerUpdate(CustomerBase):
    """Все поля опциональны при обновлении"""
    pass

class CustomerResponse(CustomerBase):
    """Поля ответа API (включая read-only)"""
    id: int = Field(..., description="Уникальный идентификатор")
    balance: float = Field(0.0, description="Текущий остаток средств")
    paid_lesson_count: int = Field(0, description="Остаток занятий")
    last_attend_date: Optional[date] = Field(None, description="Последнее посещение")
    updated_at: Optional[str] = Field(None, description="Дата изменения (DD.MM.YYYY)")
    created_at: Optional[str] = Field(None, description="Дата создания (DD.MM.YYYY)")

class CustomerFilter(ALFABaseModel):
    """Фильтрация клиентов с валидацией всех параметров"""
    # Основные параметры
    page: int = Field(0, ge=0, description="Номер страницы (с 0)")
    id: Optional[int] = None
    is_study: Optional[int] = Field(None, ge=0, le=2)
    name: Optional[str] = None
    gender: Optional[int] = Field(None, ge=0, le=2)
    phone: Optional[str] = None
    legal_type: Optional[int] = Field(None, ge=1, le=2)
    
    # Фильтры диапазонов
    age_from: Optional[int] = Field(None, ge=0, le=150)
    age_to: Optional[int] = Field(None, ge=0, le=150)
    lesson_count_from: Optional[int] = Field(None, ge=0)
    lesson_count_to: Optional[int] = Field(None, ge=0)
    balance_contract_from: Optional[float] = None
    balance_contract_to: Optional[float] = None
    balance_bonus_from: Optional[float] = None
    balance_bonus_to: Optional[float] = None
    
    # Даты с разными форматами
    next_lesson_date_from: Optional[str] = None
    next_lesson_date_to: Optional[str] = None
    last_attend_date_from: Optional[str] = None
    last_attend_date_to: Optional[str] = None
    created_at_from: Optional[str] = None
    created_at_to: Optional[str] = None
    updated_at_from: Optional[str] = None
    updated_at_to: Optional[str] = None
    dob_from: Optional[date] = None
    dob_to: Optional[date] = None
    
    # Специальные параметры
    withGroups: Optional[bool] = Field(None, alias='with_groups')
    removed: Optional[int] = Field(None, ge=0, le=2)
    customer_reject_id: Optional[int] = None

    @field_validator(
        'next_lesson_date_from', 'next_lesson_date_to',
        'last_attend_date_from', 'last_attend_date_to'
    )
    def validate_iso_dates(cls, v: str) -> str:
        if v and not re.match(r'^\d{4}-\d{2}-\d{2}$', v):
            raise ValueError("Формат даты: YYYY-MM-DD")
        return v

    @field_validator('created_at_from', 'created_at_to', 'updated_at_from', 'updated_at_to')
    def validate_dot_dates(cls, v: str) -> str:
        if v and not re.match(r'^\d{2}\.\d{2}\.\d{4}$', v):
            raise ValueError("Формат даты: DD.MM.YYYY")
        return v

    @model_validator(mode='after')
    def check_age_range(self) -> 'CustomerFilter':
        if self.age_from and self.age_to and self.age_from > self.age_to:
            raise ValueError("age_to должно быть >= age_from")
        return self
