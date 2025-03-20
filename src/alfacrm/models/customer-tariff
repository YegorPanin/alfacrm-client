from datetime import date
from typing import Optional, List, Union, Annotated
from pydantic import (
    BaseModel, 
    Field, 
    field_validator, 
    model_validator,
    BeforeValidator
)
import re

# Вспомогательная функция для валидации balance
def validate_balance(v: Union[int, List[int]]) -> Union[int, List[int]]:
    if isinstance(v, list):
        if len(v) != 2 or v[0] > v[1]:
            raise ValueError("Некорректный диапазон баланса")
    return v

class CustomerTariffBase(BaseModel):
    """Базовые поля абонемента клиента"""
    tariff_id: Optional[int] = Field(None, description="ID тарифа")
    subject_ids: Optional[List[int]] = Field(None, description="ID предметов")
    lesson_type_ids: Optional[List[int]] = Field(None, description="Типы уроков")
    is_separate_balance: Optional[bool] = None
    balance: Optional[int] = Field(None, ge=0, description="Текущий баланс")
    b_date: Optional[str] = Field(None, description="Дата начала (DD.MM.YYYY)")
    e_date: Optional[str] = Field(None, description="Дата окончания")
    note: Optional[str] = Field(None, max_length=500)

    @field_validator("b_date", "e_date")
    def validate_dates(cls, v: str) -> str:
        if v and not re.match(r"\d{2}\.\d{2}\.\d{4}", v):
            raise ValueError("Формат даты: DD.MM.YYYY")
        return v

class CustomerTariffCreate(CustomerTariffBase):
    """Обязательные поля для создания абонемента"""
    tariff_id: int = Field(...)
    customer_id: int = Field(...)
    balance: int = Field(..., ge=0)

class CustomerTariffUpdate(BaseModel):
    """Поля для обновления"""
    note: Optional[str] = Field(None, max_length=500)

class CustomerTariffResponse(CustomerTariffBase):
    """Полная модель ответа"""
    id: int
    customer_id: int
    updated_at: Optional[str] = None
    created_at: Optional[str] = None

class CustomerTariffFilter(BaseModel):
    """Фильтрация абонементов клиента"""
    id: Optional[int] = None
    tariff_id: Optional[int] = None
    is_burnable_out: Optional[bool] = None
    balance: Optional[
        Annotated[
            Union[int, List[int]], 
            BeforeValidator(validate_balance)
        ]
    ] = None
    dead: Optional[bool] = Field(
        None, 
        description="True - только архивные, False - активные"
    )
    tariff_type: Optional[int] = Field(
        None, 
        ge=1, 
        le=3, 
        description="1-поурочный, 2-помесячный, 3-недельный"
    )
    is_separate_balance: Optional[bool] = None
    page: int = Field(0, ge=0)

    @model_validator(mode="after")
    def check_date_logic(self) -> 'CustomerTariffFilter':
        if self.balance and isinstance(self.balance, list):
            if self.balance[0] < 0 or self.balance[1] < 0:
                raise ValueError("Баланс не может быть отрицательным")
        return self

class CustomerTariffDeleteParams(BaseModel):
    """Параметры для удаления абонемента"""
    id: int
    customer_id: int
