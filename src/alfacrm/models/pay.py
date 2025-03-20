from datetime import date
from typing import Optional, List
from pydantic import Field, field_validator, model_validator, ConfigDict
import re
from .base import ALFABaseModel

class PayBase(ALFABaseModel):
    """Общие поля платежа (опциональны для обновления)"""
    branch_id: Optional[int] = Field(None, description="ID филиала")
    location_id: Optional[int] = Field(None, description="ID локации")
    customer_id: Optional[int] = Field(None, description="ID клиента")
    pay_type_id: Optional[int] = Field(None, description="Тип платежа")
    pay_account_id: Optional[int] = Field(None, description="ID кассы")
    pay_item_id: Optional[int] = Field(None, description="ID статьи расхода/дохода")
    teacher_id: Optional[int] = Field(None, description="ID педагога (для ЗП)")
    commodity_id: Optional[int] = Field(None, description="ID товара")
    document_date: Optional[str] = Field(None, description="Дата платежа (DD.MM.YYYY)")
    income: Optional[float] = Field(None, description="Сумма платежа")
    payer_name: Optional[str] = Field(None, max_length=50, description="Плательщик")
    group_id: Optional[int] = Field(None, description="ID группы")
    note: Optional[str] = Field(None, description="Комментарий")

    @field_validator("document_date")
    def validate_document_date(cls, v: str) -> str:
        if v and not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
            raise ValueError("Формат даты: DD.MM.YYYY")
        return v

class PayCreate(ALFABaseModel):
    """Обязательные поля для создания платежа"""
    branch_id: int = Field(...)
    customer_id: int = Field(...)
    pay_type_id: int = Field(...)
    pay_account_id: int = Field(...)
    document_date: str = Field(...)
    income: float = Field(..., gt=0)
    payer_name: str = Field(..., max_length=50)
    note: Optional[str] = None

    @field_validator("document_date")
    def validate_create_date(cls, v: str) -> str:
        if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
            raise ValueError("Формат даты: DD.MM.YYYY")
        return v

class PayUpdate(ALFABaseModel):
    """Поля для обновления платежа"""
    income: Optional[float] = None
    payer_name: Optional[str] = None
    note: Optional[str] = None

class PayResponse(PayBase):
    """Поля ответа API с read-only данными"""
    id: int = Field(..., description="Уникальный идентификатор")
    updated_at: Optional[str] = Field(None, pattern=r"\d{2}\.\d{2}\.\d{4}")
    created_at: Optional[str] = Field(None, pattern=r"\d{2}\.\d{2}\.\d{4}")

class PayFilter(ALFABaseModel):
    """Фильтрация платежей с валидацией"""
    id: Optional[int] = None
    currency: Optional[str] = None
    location_id: Optional[int] = None
    customer_id: Optional[int] = None
    employee_id: Optional[int] = None
    pay_item_category_id: Optional[int] = None
    pay_type_id: Optional[int] = None
    pay_item_id: Optional[int] = None
    pay_account_id: Optional[int] = None
    commodity_id: Optional[int] = None
    payer_name: Optional[str] = None
    note: Optional[str] = None
    date_from: Optional[str] = None   # Формат: YYYY.MM.DD
    date_to: Optional[str] = None
    sum_from: Optional[float] = None
    sum_to: Optional[float] = None
    bonus_from: Optional[float] = None
    bonus_to: Optional[float] = None
    is_confirmed: Optional[int] = Field(None, ge=0, le=1)
    group_ids: Optional[List[int]] = None
    is_fiscal: Optional[int] = Field(None, ge=0, le=1)
    updated_at_from: Optional[str] = None   # Формат: DD.MM.YYYY
    updated_at_to: Optional[str] = None
    created_at_from: Optional[str] = None
    created_at_to: Optional[str] = None
    page: int = Field(0, ge=0)

    @field_validator("date_from", "date_to")
    def validate_ymd_dates(cls, v: str) -> str:
        if v and not re.match(r"^\d{4}\.\d{2}\.\d{2}$", v):
            raise ValueError("Формат даты: YYYY.MM.DD")
        return v

    @field_validator("updated_at_from", "updated_at_to", "created_at_from", "created_at_to")
    def validate_dmy_dates(cls, v: str) -> str:
        if v and not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
            raise ValueError("Формат даты: DD.MM.YYYY")
        return v

    @model_validator(mode="after")
    def validate_ranges(self) -> 'PayFilter':
        # Проверка диапазонов дат и сумм
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_to должно быть >= date_from")
        
        if self.sum_from and self.sum_to and self.sum_from > self.sum_to:
            raise ValueError("sum_to должно быть >= sum_from")
        
        return self

class PayFiscalSellParams(ALFABaseModel):
    """Параметры для фискализации платежа"""
    id: int = Field(..., description="ID платежа")
    type: int = Field(..., ge=1, le=2, description="1-электронный, 2-наличные")
