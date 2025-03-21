# bonus.py
from datetime import date, datetime
from typing import Literal, Optional
from pydantic import Field, field_validator, model_validator
from .base import ALFABaseModel
import re

class BonusChangeRequest(ALFABaseModel):
    """Базовый запрос на изменение бонусов (начисление/списание)"""
    customer_id: int = Field(..., gt=0, description="ID клиента")
    amount: int = Field(..., gt=0, description="Сумма бонусов")
    note: Optional[str] = Field(
        None,
        max_length=500,
        description="Комментарий к операции"
    )
    date: date = Field(
        default_factory=lambda: datetime.now().date(),
        description="Дата операции (по умолчанию сегодня)"
    )

    @field_validator("date", mode="before")
    def parse_date(cls, v: str | date) -> date:
        if isinstance(v, str):
            if not re.match(r"\d{4}-\d{2}-\d{2}", v):
                raise ValueError("Неверный формат даты. Используйте YYYY-MM-DD")
            return datetime.strptime(v, "%Y-%m-%d").date()
        return v

BonusType = Literal['add', 'spend']

class BonusHistoryFilter(ALFABaseModel):
    """Фильтр для истории операций с бонусами"""
    customer_id: int = Field(..., gt=0, description="ID клиента")
    type: Optional[BonusType] = Field(
        None,
        description="Тип операции: add - начисление, spend - списание"
    )
    date_from: Optional[date] = Field(None, description="Начальная дата периода")
    date_to: Optional[date] = Field(None, description="Конечная дата периода")
    page: int = Field(0, ge=0, description="Номер страницы")

    @model_validator(mode="after")
    def validate_dates(self) -> 'BonusHistoryFilter':
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("Дата начала не может быть позже даты окончания")
        return self

class BonusTransferRequest(ALFABaseModel):
    """Запрос на перевод бонусов между клиентами"""
    from_customer_id: int = Field(..., gt=0, description="ID клиента-отправителя")
    to_customer_id: int = Field(..., gt=0, description="ID клиента-получателя")
    amount: int = Field(..., gt=0, description="Сумма перевода")
    note: Optional[str] = Field(
        None,
        max_length=500,
        description="Комментарий к переводу"
    )

    @model_validator(mode="after")
    def check_same_customer(self) -> 'BonusTransferRequest':
        if self.from_customer_id == self.to_customer_id:
            raise ValueError("Нельзя переводить бонусы одному и тому же клиенту")
        return self

class BonusResponse(ALFABaseModel):
    """Ответ с информацией о бонусной операции"""
    id: int = Field(..., description="ID операции")
    customer_id: int = Field(..., description="ID клиента")
    amount: int = Field(..., description="Сумма операции")
    type: BonusType = Field(..., description="Тип операции")
    balance: int = Field(..., description="Текущий баланс клиента")
    date: date = Field(..., description="Дата операции")
    created_at: datetime = Field(..., description="Дата создания записи")
    note: Optional[str] = Field(None, description="Комментарий")
    lesson_id: Optional[int] = Field(
        None,
        description="ID урока (если операция связана с уроком)"
    )
    pay_id: Optional[int] = Field(
        None,
        description="ID платежа (если операция связана с оплатой)"
    )
    transfer_id: Optional[int] = Field(
        None,
        description="ID операции перевода (для межклиентских переводов)"
    )
