# CGI.py
from datetime import date
from typing import Optional
from pydantic import Field, field_validator, model_validator
from .base import ALFABaseModel
import re


class CGIBase(ALFABaseModel):
    """Базовые поля для связи клиент-группа"""
    customer_id: int = Field(..., gt=0, description="ID клиента")
    group_id: int = Field(..., gt=0, description="ID группы")
    b_date: date = Field(..., description="Дата начала (DD.MM.YYYY)")
    e_date: date = Field(..., description="Дата окончания (DD.MM.YYYY)")
    branch_id: int = Field(..., gt=0, description="ID филиала")

    @field_validator("b_date", "e_date", mode="before")
    @classmethod
    def format_dates(cls, v: date | str) -> str:
        if isinstance(v, date):
            return v.strftime("%d.%m.%Y")
        if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
            raise ValueError("Неверный формат даты. Используйте DD.MM.YYYY")
        return v

    @model_validator(mode="after")
    def validate_date_range(self) -> 'CGIBase':
        b_date = date.fromtimestamp(
            date(*map(int, self.b_date.split(".")[::-1])).timestamp()
        )
        e_date = date.fromtimestamp(
            date(*map(int, self.e_date.split(".")[::-1])).timestamp()
        )

        if e_date < b_date:
            raise ValueError("Дата окончания не может быть раньше даты начала")
        return self


class CGICreate(CGIBase):
    """Модель для создания связи клиент-группа"""
    pass


class CGIUpdate(ALFABaseModel):
    """Модель для обновления связи"""
    b_date: Optional[date] = None
    e_date: Optional[date] = None
    branch_id: Optional[int] = Field(None, gt=0)

    @field_validator("b_date", "e_date", mode="before")
    @classmethod
    def format_optional_dates(cls, v: date | str | None) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, date):
            return v.strftime("%d.%m.%Y")
        if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
            raise ValueError("Неверный формат даты. Используйте DD.MM.YYYY")
        return v


class CGIResponse(CGIBase):
    """Модель ответа с сервера"""
    id: int = Field(..., description="ID связи")
    updated_at: str = Field(..., description="Дата обновления")
    created_at: str = Field(..., description="Дата создания")


class CGICustomerFilter(ALFABaseModel):
    """Фильтр для получения групп клиента"""
    customer_id: int = Field(..., gt=0, description="ID клиента")
    b_date: Optional[date] = None
    e_date: Optional[date] = None
    page: int = Field(0, ge=0)

    @field_validator("b_date", "e_date", mode="before")
    @classmethod
    def validate_dates(cls, v: date | str | None) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, date):
            return v.strftime("%d.%m.%Y")
        if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
            raise ValueError("Формат даты: DD.MM.YYYY")
        return v


class CGIGroupFilter(ALFABaseModel):
    """Фильтр для получения клиентов группы"""
    group_id: int = Field(..., gt=0, description="ID группы")
    b_date: Optional[date] = None
    e_date: Optional[date] = None
    page: int = Field(0, ge=0)

    @field_validator("b_date", "e_date", mode="before")
    @classmethod
    def validate_dates(cls, v: date | str | None) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, date):
            return v.strftime("%d.%m.%Y")
        if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", v):
            raise ValueError("Формат даты: DD.MM.YYYY")
        return v
